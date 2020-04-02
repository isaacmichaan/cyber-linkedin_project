import requests
from header_parser import headers_parser
import json
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
import mysql.connector as mariadb

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
#client = MongoClient("mongodb+srv://isaacmichaan1:11Yossef@cluster0-gvxqb.gcp.mongodb.net/test?retryWrites=true&w=majority")
#db=client.peopleList

raw_headers = '''User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: application/vnd.linkedin.normalized+json+2.1
Accept-Language: en-US,en;q=0.5
x-li-lang: en_US
x-li-track: {"clientVersion":"1.5.*","osName":"web","timezoneOffset":-5,"deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1}
x-li-page-instance: urn:li:page:d_flagship3_feed;WCZGg/ngS9O3XQqJkho0rQ==
csrf-token: ajax:1601749915603344439
x-restli-protocol-version: 2.0.0
Cookie: bcookie="v=2&9d9cdf29-299a-4c97-8577-1f84b6a39d84"; bscookie="v=1&20200301175353577d1c86-d141-4985-86e5-b45e383ea55aAQGhbXXMZCBdgDthFx2VSnaxm3-iyhus"; lissc=1; JSESSIONID="ajax:1601749915603344439"; lidc="b=SGST08:g=11:u=1:i=1583085957:t=1583172357:s=AQHrYUy_ywFKHnmA8i1RfbLan-g1d0J5"; li_at=AQEDASzim18Eb0s2AAABcJc7wO4AAAFwu0hE7k4ATktOVjz1xGEVWVveqnk2lmidulS_TLPu28EDL17hwhk3_f5jPlVA_4pvRztsyObVx2kcRML1GYjFflUbZ5uMg6AErHjaS6jUTcwHwIjP1nAgAhT_; liap=true; sl=v=1&2G0bK; lang=v=2&lang=pt-br; _ga=GA1.2.1780157534.1583085316; UserMatchHistory=AQIsOHIRSl6LgwAAAXCXPTyl_MFRv81VmYn7lLdOv-DYTAMyhalx7mcWKDDGHYhy3X7d1Ff5OVINim5Gn3DdhJhTSh_kQv61170rqexAI3f4AZb_eGO63YhwqmA85XSeYip575_avftNlksZqnARQKFBChnx1GkAx4SIM5UtOHetQ-wVo4aPrwEsWAB3BrNct6lnqrB3dWoCLkLYAJC7Bgrt5Si3bry-; li_sugr=2c169dc1-485b-4758-84cc-9395f53ae5f6; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-1303530583%7CMCIDTS%7C18323%7CMCMID%7C12446057456421928572156768684795867043%7CMCAAMLH-1583690120%7C6%7CMCAAMB-1583690120%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1583092519s%7CNONE%7CMCCIDH%7C-1868004826%7CvVersion%7C3.3.0; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; li_oatml=AQFegNQ0Z2-g6wAAAXCXPQPBUv3tFzeb6FVQFX7KL9UDZTYoBSc8Vt2ym3akPBhe7Cl8LQT-9_iBOWB2KogKyskV97sp7T5b; aam_uuid=12639869210614364342099045271697841256; _guid=ec270791-8e3d-4f1a-a0c4-c2c485139d62'''


class Linkedin:
	def __init__(self):
		self.headers = headers_parser(raw_headers)
		self.url_company = 'https://www.linkedin.com/voyager/api/typeahead/hitsV2'
		self.url_people = 'https://www.linkedin.com/search/results/people'
		self.peopleList = []
		self.cursor = ''
		self.mariadb_connection = ''

	def db_connection(self, databases=''):
		self.mariadb_connection = mariadb.connect(user='root', password='toor')
		self.cursor = self.mariadb_connection.cursor()
		# create database
		if not databases:
			databases = input('enter database name: ')
		sql = 'CREATE OR REPLACE DATABASE ' + databases
		self.cursor.execute(sql)

		# connect database and create table
		self.mariadb_connection = mariadb.connect(user='root', password='toor', database=databases)
		self.cursor = self.mariadb_connection.cursor()
		sql = "CREATE OR REPLACE TABLE linkedin (name VARCHAR(1000))"
		self.cursor.execute(sql)

	def choice(self, jres):
		#c = int(input('Choose number only from COMPANY types: '))
		c = 2
		if jres['data']['elements'][c]['type'] != 'COMPANY':
			print('[-] type is not COMPANY')
			return self.choice(jres)
		return re.findall(r'\d+', jres['data']['elements'][c]['targetUrn'])

	def company(self, company=''):
		if not company:
			company = input("Enter Company: ")
		self.db_connection(company)
		params = {
				'keywords': company,
				'origin': 'GLOBAL_SEARCH_HEADER',
				'q': 'blended'
			}
		res = requests.get(self.url_company, params=params, headers=self.headers)
		jres = json.loads(res.text)
		#for num, ele in enumerate(jres['data']['elements']):
			#print(num, ele['text']['text'] + ' - ' + ele['type'])
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
						val = (j['title']['text'], )
						try:
							self.cursor.execute("INSERT INTO linkedin (name) VALUES (%s)", val)
							self.mariadb_connection.commit()
						except:
							pass
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
