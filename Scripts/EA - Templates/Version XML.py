#!/usr/bin/python

"""
Determines if a product is at least a specified Version by reading (text) content from a Tag in XML file at a specific path.
The Tag in the file may be specified to obtain the product's version.
Results may (optionally) be limited to a range, when the property list is used for multiple major releases of the product.
Returns 'Older' if an older version of the product is found.
Returns 'Equal' if the same version of a product is found.
Returns 'Newer' if a newer version of the product is found.
Returns 'N/A' if the product is not found.
"""

# Path to plist to read version key from [required]
Source = 'PATH'
# Tag in source to read version string from [required]
Tag = 'TAG'
# Version to test for [required]
Version = 'VERSION'
# Range limit for plist version [optional]
# Range = ['MIN', 'MAX']

# Required modules
from os.path import isabs, isfile
from pkg_resources import parse_version
from re import sub
from xml.etree.ElementTree import parse

# Read Tag's Value as String from Source
def read_xml(s, t):
	try:
		v = parse(s).getroot().find('.//' + t).text
	except:
		v = ''
	return v

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
	Source
except:
	print '<result>Error: Source path not defined</result>'
	exit(1)
try:
	Tag
except:
	print '<result>Error: No Tag specified</result>'
	exit(1)
try:
	Version
except:
	print '<result>Error: No Version specified</result>'
	exit(1)
try:
	Range
except:
	Range = None

# Validate Source
if (not isabs(Source)):
	print '<result>Error: Source path is invalid</result>'
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

# Check Installed Version
if (not isfile(Source)):
	Result = 'N/A'
else:
	Installed = read_xml(Source, Tag)
	Installed = rationalise_version(Installed)
	if (Installed == ''):
		Result = 'Error: Reading installed version'
	else:
		Result = compare_versions(Installed, Version)
		if (Range):
			if (version_in_range(Installed, Range) == False):
				Result = 'N/A'

# Output Result
print '<result>' + Result + '</result>'
exit(0)