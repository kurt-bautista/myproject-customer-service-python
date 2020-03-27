import pytest
import unittest
import boto3
import sys 
from moto import mock_dynamodb2
from flaskr.customer_table_client import getAllCustomers, getCustomer, \
	createCustomer, updateCustomer, deleteCustomer
import json
import os

# Load customers static db from json file
THIS_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
my_file = os.path.join(THIS_FOLDER, "tests", 'customers.json')

with open(my_file) as f:
    customers = json.load(f)

class TestDynamo(unittest.TestCase):
		def setUp(self):
			self.table_name = 'customers'
			# load the test data from test/customers.json
			self.customer_data = {
				"customers": customers
			}
			self.test_customer_id = '4e53920c-505a-4a90-a694-b9300791f0ae'
			self.test_delete_customer_id = "2b473002-36f8-4b87-954e-9a377e0ccbec"
			self.test_customer_dict = {
					"firstName": "Mikhael",
					"lastName": "Cuazon",
					"email": "Mikhael@cpanel.net",
					"userName": "Mikhael@cpanel.net",
					"birthDate": "January 17, 1996",
					"gender": "Male",
					"custNumber": "0999962019111902",
					"cardNumber": "6236332019111900012",
					"phoneNumber": "97667322",
					"createdDate": "March 27, 2020",
					"updatedDate": "March 27, 2020",
					"profilePhotoUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/PICA.jpg/600px-PICA.jpg"
			}

		@mock_dynamodb2
		def __moto_dynamodb_setup(self):
				table_name = 'customers'
				dynamodb = boto3.resource('dynamodb', 'ap-southeast-2')
				table = dynamodb.create_table(
						TableName=table_name,
						KeySchema=[
								{
										'AttributeName': 'customerId',
										'KeyType': 'HASH'
								},
						],
						AttributeDefinitions=[
								{
										'AttributeName': 'customerId',
										'AttributeType': 'S'
								},

						],
						ProvisionedThroughput={
								'ReadCapacityUnits': 5,
								'WriteCapacityUnits': 5
						}
				)
				for customer in self.customer_data['customers']:
						item = {}
						item['customerId'] = customer['customerId']
						item['firstName'] = customer['firstName']
						item['lastName'] = customer['lastName']
						item['email'] = customer['email']
						item['userName'] = customer['userName']
						item['birthDate'] = customer['birthDate']
						item['gender'] = customer['gender']
						item['custNumber'] = customer['custNumber']
						item['cardNumber'] = customer['cardNumber']
						item['phoneNumber'] = customer['phoneNumber']
						item['createdDate'] = customer['createdDate']
						item['updatedDate'] = customer['updatedDate']
						item['profilePhotoUrl'] = customer['profilePhotoUrl']								
						table.put_item(Item=item)

		@mock_dynamodb2
		def test_get_all_customers(self):
				self.__moto_dynamodb_setup()
				customers = getAllCustomers()
				self.assertEqual(json.dumps(self.customer_data), customers)

		@mock_dynamodb2
		def test_get_customer(self):
				self.__moto_dynamodb_setup()
				customer = getCustomer(self.test_customer_id)
				testCustomer = [c for c in self.customer_data['customers'] if c['customerId'] == self.test_customer_id]				
				# check if the data matches the sample data
				self.assertEqual(json.loads(customer)['customers']['data'], testCustomer[0])
				# check if the status is GET OK
				self.assertEqual(json.loads(customer)['customers']['status'], "GET OK")

		@mock_dynamodb2
		def test_create_customer(self):
				self.__moto_dynamodb_setup()
				customer = createCustomer(self.test_customer_dict)
				# check if the status is CREATED OK
				self.assertEqual(json.loads(customer)['customers']['status'], "CREATED OK")
				createdId = json.loads(customer)['customers']['data']['customerId']
				customerGet = getCustomer(createdId)
				# check if the data key matches the created customer object
				self.assertEqual(json.loads(customer)['customers']['data'], json.loads(customerGet)['customers']['data'])

		@mock_dynamodb2
		def test_update_customer(self):
				self.__moto_dynamodb_setup()
				customer = updateCustomer(self.test_customer_id, self.test_customer_dict)
				# check if the status is UPDATED OK
				self.assertEqual(json.loads(customer)['customers']['status'], "UPDATED OK")
				updatedId = json.loads(customer)['customers']['data']['customerId']
				customerGet = getCustomer(updatedId)
				# check if the data key matches the updated customer object
				self.assertEqual(json.loads(customer)['customers']['data'], json.loads(customerGet)['customers']['data'])

		@mock_dynamodb2
		def test_delete_customer(self):
				self.__moto_dynamodb_setup()
				customer = deleteCustomer(self.test_delete_customer_id)
				# check if the status is DELETED OK
				self.assertEqual(json.loads(customer)['customers']['status'], "DELETED OK")
				deletedId = json.loads(customer)['customers']['data']['customerId']
				customerGet = getCustomer(deletedId)
				# check if the customerId matches the deleted object
				self.assertEqual(deletedId, self.test_delete_customer_id)
				# check if the customer exists will fail if existing
				self.assertEqual(json.loads(customerGet)['customers']['status'], "Customer not found")