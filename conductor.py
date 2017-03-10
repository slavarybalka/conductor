#python 2.7

import requests
import time
import hashlib
import sys
import csv

def compute_signature(api_key, shared_secret):
	m = hashlib.md5()
	m.update(api_key)
	m.update(shared_secret)
	epoch_sec = int(time.time())
	m.update(str(epoch_sec))
	digest = m.digest()
	hex_digest = digest.encode('hex')
	return hex_digest


# retrieve API KEY and SECRET from file
with open('/Users/slava.rybalka/Documents/Pyscripts/SEO_scripts/API_credentials.txt') as file_object:
	contents = file_object.read()
	conductor_api_key = contents.split('\n')[0].split(': ')[1]
	conductor_secret = contents.split('\n')[1].split(': ')[1]
	semrush_api_key = contents.split('\n')[2].split(': ')[1]

conductor_signature = compute_signature(conductor_api_key, conductor_secret)


combined_data = {}
export_data = []

# substitute account_id and property_id with the ones you need
r = requests.get("https://api.conductor.com/v3/12808/web-properties/59458/rank-sources/1/tp/CURRENT/serp-items?apiKey=" + conductor_api_key + "&sig=" + conductor_signature)

# retrieving keywords in striking distance
for elem2 in r.json():
	#print elem2
	if ("/programs/" in elem2['targetUrl'] or elem2['targetUrl'] == 'http://academicpartnerships.uta.edu') and elem2['ranks']['TRUE_RANK'] < 20:
		if elem2['ranks']['TRUE_RANK'] > 10:
			combined_data[str(elem2['trackedSearchId'])] = [elem2['ranks']['TRUE_RANK'], elem2['targetUrl']]

#print combined_data

t = requests.get("https://api.conductor.com/v3/accounts/12808/web-properties/59458/tracked-searches?apiKey=" + conductor_api_key + "&sig=" + conductor_signature)
for elem1 in t.json():
	#print elem1
	for key, value in combined_data.iteritems():
		if elem1['trackedSearchId'] == key:
			combined_data[key].append(elem1['queryPhrase'])

#print combined_data

# SEMRush: "This report provides an extended list of related keywords, synonyms, and variations relevant to a queried term in a chosen database."

for key, value in combined_data.iteritems():
	# setting a delay between SEMRush requests
	time.sleep(3)										
	
	s = requests.get('http://api.semrush.com/?type=phrase_related&key=' + semrush_api_key + '&display_limit=10&export_columns=Ph,Nq&phrase=' + value[2] + '&database=us')
	result = s.text.split('\r') 						# getting related searches for each keyword
	if result == [u'ERROR 50 :: NOTHING FOUND']:		# if nothing is found then just skip it
		pass
	else:
		print "\nSource keyword:", value[2]
		print "\nRelated keywords:"
		
		#retrieve the contents of the URL
		pr = requests.get(value[1])

		for item in result[1:]:							# if some related keywords are returned then 
			semrush_list = item.strip().split(';')

			# checking if the keyword exists on page
			if semrush_list[0] not in pr.text:
			#if it doesn't exist, append it to the list
				export_data.append([value[2], semrush_list[0], semrush_list[1], value[1]])



print export_data

with open('striking_distance_recommendations.csv', 'wb') as csvfile:
    x_writer = csv.writer(csvfile, delimiter=',')
    x_writer.writerow(['Source Keyword','Related Keyword','Search Volume','Page URL']) #writing headers
    for entry in export_data:
    	#print export_data
        x_writer.writerow(entry)















