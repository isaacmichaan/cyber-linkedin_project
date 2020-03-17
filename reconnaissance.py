from linkedin import Linkedin
from google_dork import Google
from subdomain import Subdomain
from whois_pocs import Whois

#variables
company = input("Enter Company: ")
domain = (company + '.com')
intext = ('@' + domain)
pages = 3
path = '/root/Documents/python_codes/PyCharm/Reconnaissance/subdomains.txt'
db_name = company

# print and save 100 user_names
l = Linkedin()
l.company(company)

# search for emails in first #3 google pages
g = Google()
g.google_search(domain, intext, pages)

# print and save subdomains (may take a while)
s = Subdomain()
s.main(domain, path, db_name)

# save contacts (may take a while from Start to Finish)
w = Whois()
w.domain_name(db_name, domain)
