#!/usr/bin/python3
import mysql.connector as mariadb
from header_parser import headers_parser
from urllib.parse import urlparse
import requests
import json
from bs4 import BeautifulSoup
import re

headers = '''User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Connection: keep-alive
Cache-Control: max-age=0'''


class Whois:
	def __init__(self):
		self.check_if_lastname_exists = []
		self.cursor = ''
		self.mariadb_connection = ''

	def db_connection(self, database):
		if not database:
			#connect to database and create table
			database = input('enter database name: ')
		self.mariadb_connection = mariadb.connect(user='root', password='toor', database=database)
		self.cursor = self.mariadb_connection.cursor()
		sql = "CREATE OR REPLACE TABLE contacts (name VARCHAR(1000), lastname VARCHAR(1000), email VARCHAR(1000), phone VARCHAR(1000), city VARCHAR(1000), state VARCHAR(1000), country VARCHAR(1000))"
		self.cursor.execute(sql)

	def contacts(self, soup):
		#go over all contacts and save on database
		for tag in soup.find_all("a", href=re.compile("/rest/poc/")):
			res = requests.get(tag['href'])
			soup = BeautifulSoup(res.content, 'html.parser')

			#saving info to variables
			lastname = (re.findall('Name[a-zA-Z0-9_.+-]+',soup.text)[0].partition('Name')[2])
			if lastname in self.check_if_lastname_exists:
				continue
			self.check_if_lastname_exists.append(lastname)

			name = re.findall(', [A-Z0-9_.+-]+',soup.text)[0].partition(', ')[2]
			if len(name) < 3:
				name = ''
			try:
				email = (re.findall('Email[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',soup.text)[0].partition('Email')[2])
				phone = (re.findall('Phone[a-zA-Z0-9_.+-]+',soup.text)[0].partition('Phone')[2])
				city = (re.findall('City[a-zA-Z0-9_.+-]+',soup.text)[0].partition('City')[2])
				state = (re.findall('State/Province[a-zA-Z0-9_.+-]+',soup.text)[0].partition('State/Province')[2])
				country = (re.findall('Country[a-zA-Z0-9_.+-]+',soup.text)[0].partition('Country')[2])
			except:
				continue

			#saving info to database
			val = (name, lastname, email, phone, city, state, country)
			try:
				self.cursor.execute("INSERT INTO contacts (name, lastname, email, phone, city, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s)", val)
				self.mariadb_connection.commit()
			except:
				pass

	def domain_name(self, db='', domain=''):
		self.db_connection(db)

		#change handshake default cypher
		requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

		if not domain:
			#domain to gather contact info
			domain = input('insert domain: ')
		url = 'http://whois.arin.net/rest/pocs;domain=%s' % (domain)
		res = requests.get(url, headers=headers_parser(headers))
		soup = BeautifulSoup(res.content, 'html.parser')

		print('Start')
		self.contacts(soup)
		print('Finish')

		print(self.cursor.rowcount, "record inserted.")


if __name__ == "__main__":
	test = Whois()
	test.domain_name()
