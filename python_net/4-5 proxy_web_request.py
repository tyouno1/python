import urllib

URL = 'https://www.github.com'
PROXY_ADDRESS = "x.x.x.x"

if __name__ == '__main__':
	resp = urllib.urlopen(URL, proxies = {"http" : PROXY_ADDRESS})
	print "Proxy server returns response headers:%s" % resp.headers