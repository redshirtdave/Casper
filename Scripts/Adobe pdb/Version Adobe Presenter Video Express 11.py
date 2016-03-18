#!/usr/bin/python

"""
Determines if an Adobe product is at least a specified Version by querying the pdb.db database for a productName and payloadName.
Results may (optionally) be limited to a range of versions when the productName is not unique.
Returns 'Older' if an older version of the product is found.
Returns 'Equal' if the same version of a product is found.
Returns 'Newer' if a newer version of the product is found.
Returns 'N/A' if the product is not found.
"""

# productName in database to search for [required]
productName = 'Adobe Presenter Video Express 11'
# payloadName for product [optional]
# payloadName = 'PAYLOAD'
# Version to test for [required]
Version = '11.0.0'
# Range limit for product version [optional]
# Range = ['MIN', 'MAX']
# Path to pdb.db database containing installed product information [required]
pdb = '/Library/Application Support/Adobe/caps/pdb.db'

# Required modules
from sqlite3 import connect
from os.path import isfile
from pkg_resources import parse_version
from re import sub

# Search for productName in pdb
def query_db_product(db, product, payload):
	c = connect(db).cursor()
	try:
		c.execute('SELECT version FROM payloads WHERE productName LIKE "' + product \
					+ '" OR productName LIKE "' + product + '_%_' + str(payload) + '"')
		q = c.fetchall()
		connect(db).close()
	except:
		q = None
	r = []
	if (q):
		for i in q:
			r.append(i[0].encode('ascii','ignore'))
	return r

# Rationalise Version String
def rationalise_version(v):
	# Convert to lowercase
	v = v.lower()
	# Remove leading non-numeric characters
	v = sub('^[^0-9]*', '', v)
	# Remove trailing spaces
	v = sub(' *$', '', v)
	# Replace commas with periods
	v = sub(',', '.', v)
	# Remove 'dodgy' characters
	v = sub('[^a-z0-9 .-]', '', v)
	return v

# Compare Version Strings
def compare_versions(v1, v2):
	if (parse_version(v1) < parse_version(v2)):
		r = 'Older'
	elif (parse_version(v1) == parse_version(v2)):
		r = 'Equal'
	elif (parse_version(v1) > parse_version(v2)):
		r = 'Newer'
	return r

# Version in Range
def version_in_range(v, r):
	r = parse_version(r[1]) > parse_version(v) >= parse_version(r[0])
	return r

# Initialise variables
try:
	productName
except:
	print '<result>Error: productName not defined</result>'
	exit(1)
try:
	payloadName
except:
	payloadName = None
try:
	Version
except:
	print '<result>Error: No Version specified</result>'
	exit(1)
try:
	Range
except:
	Range = None
try:
	pdb
except:
	print '<result>Error: pdb not defined</result>'
	exit(1)

# Validate Version
Version = rationalise_version(Version)
if (Version == ''):
	print '<result>Error: Version is invalid</result>'
	exit(1)

# Validate Range
if (Range):
	if (len(Range) != 2):
		print '<result>Error: Range requires two values</result>'
		exit(1)
	else:
		Range[0] = rationalise_version(Range[0])
		if (Range[0] == ''):
			print '<result>Error: Range minimum is invalid</result>'
			exit(1)
		Range[1] = rationalise_version(Range[1])
		if (Range[1] == ''):
			print '<result>Error: Range maximum is invalid</result>'
			exit(1)
		if (compare_versions(Range[0], Range[1]) != 'Older'):
			print '<result>Error: Range minimum is greater than maximum</result>'
			exit(1)
		if (version_in_range(Version, Range) == False):
			print '<result>Error: Version is not within Range</result>'
			exit(1)


# Check Installed Version(s)
Results = []
if (isfile(pdb)):
	# Query database for matching records
	Records = query_db_product(pdb, productName, payloadName)
	if (len(Records) == 0):
		Results.append('N/A')
	else:
		for i, Installed in enumerate(Records):
			Installed = rationalise_version(Installed)
			if (Installed == ''):
				Results.append('Error: Reading installed version')
			else:
				Results.append(compare_versions(Installed, Version))
			if (Range):
				if (version_in_range(Installed, Range) == False):
					Results[i] = 'N/A'
else:
	Results.append('N/A')

if (len(Results) == 1):
	Result = Results[0]
elif ('Newer' in Results):
	Result = 'Newer'
elif ('Equal' in Results):
	Result = 'Equal'
elif ('Older' in Results):
	Result = 'Older'
elif ('N/A' in Results):
	Result = 'N/A'
else:
	Result = 'Error: Reading installed version'

# Output Result
print '<result>' + Result + '</result>'
exit(0)
