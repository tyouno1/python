import requests
import urllib
import urllib2

ID_USERNAME = 'signup-user-name'
ID_EMAIL = 'signup-user-email'
ID_PASSWORD = 'signup-user-password'
USERNAME = 'yourusername'
EMAIL = 'your@mail.com'
PASSWORD = 'yourpassword'
SIGNUP_URL = 'https://twitter.com/account/create'

def submit_form():
	""" Submit a form """
	payload = {
		ID_USERNAME : USERNAME,
		ID_EMAIL : EMAIL,
		ID_PASSWORD : PASSWORD
	}

	#make a GET request
	resp = requests.get(SIGNUP_URL)
	print "Reponse to GET request:%s" % resp.content

	#send a POST request
	resp = requests.post(SIGNUP_URL, payload)
	print "Headers from a POST request:%s" % resp.Headers
	#print "HTML Response:%s" % resp.read()

if __name__ == '__main__':
	submit_form()