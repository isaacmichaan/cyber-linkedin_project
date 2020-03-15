from pymongo import MongoClient
import re

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient("mongodb+srv://isaacmichaan1:11Yossef@cluster0-gvxqb.gcp.mongodb.net/test?retryWrites=true&w=majority")
db=client.peopleList

emails = ['isaac.michaan@hotmail.com', 'alex.klein@hotmail.com', 'uriel.max@hotmail.com', 'bill.gates@hotmail.com']

class Linking:
	def __init__(self):
		self.peopleList = list(db.test.find({}))

	# Check email list and define rule how to split
	def rule(self, emails):
		for email in emails:
			name = (re.findall(r"[\w]+", email)[0].capitalize() + ' ' + re.findall(r"[\w]+", email)[1].capitalize())
			db.test.find_one_and_update(
				{'name': name},
				{ "$set": { 'name':name, 'email': email} },
			)
if __name__ == "__main__":
	test = Linking()
	test.rule(emails)
