from tqdm import tqdm
import urllib.request
import os.path
import sys

for i in tqdm(range(1630600)):
	if os.path.isfile("cache/{}.json".format(i)) == True:
		continue

	try:
		urllib.request.urlretrieve("https://derpibooru.org/images/{}.json".format(i), "cache/{}.json".format(i))
	except urllib.error.HTTPError as e:
		if e.code == 404:
			pass
		else:
			sys.exit(-2)
	except urllib2.URLError as e:
		sys.exit(-1)
