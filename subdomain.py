#!/usr/bin/env python3
import whois
import dns.resolver
from threading import Thread
import argparse
import sys
from queue import Queue
import mysql.connector as mariadb
import socket

MAX_SUBDOMAIN_LENGTH = 63
FILEMODE_READ = "r"
FILEMODE_APPEND = "a"
NXDOMAIN = "NXDOMAIN"
RECORD_TYPE_A = "A"
RECORD_TYPE_AAAA = "AAAA"
RECORD_TYPE_MX = "MX"
RECORD_TYPE_NS = "NS"
GOOGLE_NAME_SERVER = "8.8.8.8"

C_RED = "\033[1;31m"
C_RESET = "\033[0m"
C_YELLOW = "\033[1;33m"
C_GREEN = "\033[1;32m"
C_WHITE = "\033[1;37m"


class Subdomain:
	def __init__(self):
		self.q = Queue()
		self.cursor = ''

	# print messages
	def print_err(self, message):
		print(f"{C_RED}[-]{C_RESET} ERROR: {message}")
		sys.exit(1)

	def print_notif(self, message):
		print(f"{C_YELLOW}[!]{C_RESET} {message}")

	def print_yay(self, message):
		print(f"{C_GREEN}[+]{C_RESET} {message}")

	def resolve(self, root, name_server, outfile):
		while True:
			# get the subdomain from the queue
			sub = self.q.get()

			# scan the subdomain
			resolver = dns.resolver.Resolver()
			resolver.nameservers = [name_server, ]
			domain = sub + "." + root

			# probably should check other records (A, AAAA, MX, NS), but this will do for now.
			try:
				answers = resolver.query(domain, RECORD_TYPE_A).rrset[0]
				self.print_yay(f"{domain} => {answers}")
				reversed_dns = []

				try:
					reversed_dns = socket.gethostbyaddr(str(answers))
				except:
					reversed_dns.append('')

				val = (domain, str(answers), reversed_dns[0])

				try:
					self.cursor.execute("INSERT INTO servers (domain, address, reverse_dns) VALUES (%s, %s, %s)", val)
				except:
					pass

				if outfile:
					with open(outfile, "a") as f:
						f.write("http://" + domain + ":" + str(answers) + "\n")
			except:
				pass

			# we're done with scanning that subdomain
			self.q.task_done()

	def runBrute(self, domain, wordlist, resolver, outfile, n_threads):
		self.print_notif("Beginning brute force...")

		# Parse Word List
		file = open(wordlist)
		content = file.read()
		wordlists = content.splitlines()

		# for sub in wordlists:
		for sub in wordlists:
			self.q.put(sub)

		for t in range(int(n_threads)):
			# start all threads
			worker = Thread(target=self.resolve, args=(domain, resolver, outfile))
			# daemon thread means a thread that will end when the main thread ends
			worker.daemon = True
			worker.start()


	def main(self):
		parser = argparse.ArgumentParser(description="Brute force subdomains of a specified domain.")
		parser.add_argument('-d', nargs='?', metavar='domain',
							help='Specifies the target parent domain you want to enumerate the subdomains of.')
		parser.add_argument('-w', nargs='?', metavar='wordlist',
							help='Specifies the wordlist to use for subdomain brute force.')
		parser.add_argument('-r', nargs='?', metavar='resolver',
							help='Specifies the IP address of the resolver to use (8.8.8.8 by default).')
		parser.add_argument('-o', nargs='?', metavar='outfile',
							help='Specifies a file to log results to in addition to standard output.')
		parser.add_argument('-t', nargs='?', metavar='thread',
							help='Specifies the number of threads.')

		args = parser.parse_args()

		domain = ""
		if not args.d:
			domain = input("Enter domain name: ")
			#self.print_err("A parent domain must be specified with the -d option.")
		elif args.d:
			domain = args.d

		if not args.w:
			args.w = input("Enter path to wordlist directory: ")
			#self.print_err("A wordlist must be specified with the -w option.")

		resolver = ""
		if not args.r:
			# defaults to using Google's Name Server. Probably should build in some redundancy here, but
			# I've never actually seen 8.8.8.8 go down, so I'm not too worried about this.
			resolver = GOOGLE_NAME_SERVER
		elif args.r:
			resolver = args.r

		if not args.t:
			args.t = 30

		#create database
		mariadb_connection = mariadb.connect(user='root', password='toor')
		self.cursor = mariadb_connection.cursor()
		databases = input("database name: ")
		sql = 'CREATE OR REPLACE DATABASE ' + databases
		self.cursor.execute(sql)

		#create table
		mariadb_connection = mariadb.connect(user='root', password='toor', database=databases)
		self.cursor = mariadb_connection.cursor()
		sql = "CREATE OR REPLACE TABLE servers (domain VARCHAR(1000) NOT NULL, address VARCHAR(1000) NOT NULL, reverse_dns VARCHAR(1000))"
		self.cursor.execute(sql)

		try:
			self.runBrute(domain, args.w, resolver, args.o, args.t)
		except KeyboardInterrupt:
			self.print_notif("Exiting...")
			sys.exit(2)

		self.q.join()
		mariadb_connection.commit()
		print(self.cursor.rowcount, "record inserted.")

if __name__ == "__main__":
	test = Subdomain()
	test.main()
