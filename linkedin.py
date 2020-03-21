import requests
from header_parser import headers_parser
import json
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
#client = MongoClient("mongodb+srv://:@cluster0-gvxqb.gcp.mongodb.net/test?retryWrites=true&w=majority")
#db=client.peopleList

raw_headers = '''User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: application/vnd.linkedin.normalized+json+2.1
Accept-Language: en-US,en;q=0.5
x-li-lang: en_US
x-li-track: {"clientVersion":"1.5.*","osName":"web","timezoneOffset":-5,"deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1}
x-li-page-instance: urn:li:page:d_flagship3_feed;WCZGg/ngS9O3XQqJkho0rQ==
csrf-token: ajax:1601749915603344439
x-restli-protocol-version: 2.0.0
Cookie: YOUR COOKIES COMES HERE'''

class Linkedin:
	def __init__(self):
		self.headers = headers_parser(raw_headers)
		self.url_company = 'https://www.linkedin.com/voyager/api/typeahead/hitsV2'
		self.url_people = 'https://www.linkedin.com/search/results/people'
		self.peopleList = []

	def choice(self, jres):
		c = int(input('Choose number only from COMPANY types: '))
		if jres['data']['elements'][c]['type'] != 'COMPANY':
			print('[-] type is not COMPANY')
			return self.choice(jres)
		return re.findall(r'\d+', jres['data']['elements'][c]['targetUrn'])

	def company(self):
		company = input("Enter Comapny: ")
		params = {
				'keywords': company,
				'origin': 'GLOBAL_SEARCH_HEADER',
				'q': 'blended'
			}
		res = requests.get(self.url_company, params=params, headers=self.headers)
		jres = json.loads(res.text)
		for num, ele in enumerate(jres['data']['elements']):
			print(num, ele['text']['text'] + ' - ' + ele['type'])
		id = self.choice(jres)
		self.people(id)
		#self.save()

	def people(self, id):
		for i in range(1,11):
			params = {
					'facetCurrentCompany':id,
					'page':str(i)
				}
			res = requests.get(self.url_people, params=params, headers=self.headers)
			soup = BeautifulSoup(res.content, 'html.parser')
			tree = soup.find_all("code")[14]
			oJson = json.loads(tree.text)['data']['elements']
			try:
				for i in oJson:
					for j in i['elements']:
						print(j['title']['text'])
						self.peopleList.append({
							"name": j['title']['text'],
						})
			except:
				pass

	#def save(self):
		#db.test.delete_many({})
		#db.test.insert_many(self.peopleList)

if __name__ == "__main__":
	test = Linkedin()
	test.company()
