#verify if email exists
import requests

def email_verify():
	headers = {
    		'Authorization': 'bearer 58c15313-37b0-4246-98e7-c6b1f91d4acc',
		}
	email = input('Enter Email: ')
	params = {
    		'email':email,
	}
	res = requests.get('https://isitarealemail.com/api/email/validate', headers=headers, params=params)

	if 'invalid' in res.text:
		return 0
	return 1
