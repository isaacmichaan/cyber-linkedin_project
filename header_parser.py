# a help function to split the headers and transforming in a dictionary to be able to use when doing a request
def headers_parser(raw_headers):
	headers = {}
	for line in raw_headers.split('\n'):
		x = line.split(': ')
		headers[x[0]] = x[1]
	return headers
