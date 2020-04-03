from scapy.all import *

def ports(dst):
	port = [80, 443, 8080, 22, 445, 3389]
	open = []
	for p in port:
		res = sr1(IP(dst=dst)/TCP(dport=p), timeout=1, verbose=False)
		if res:
			#print('[+] Port is open')
			open.append(p)
		#else:
			#print('[-] Port is closed')
	return open
