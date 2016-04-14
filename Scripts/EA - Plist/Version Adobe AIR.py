#!/usr/bin/python

"""
Determines if a product is at least a specified Version by reading a Key from a property list at a specific path.
The Key in the property list file may be specified to obtain the product's version.
Typically the Key is 'CFBundleShortVersionString' or 'CFBundleVersion', although a custom Key may be specified.
Results may (optionally) be limited to a range, when the property list is used for multiple major releases of the product.
Returns 'Older' if an older version of the product is found.
Returns 'Equal' if the same version of a product is found.
Returns 'Newer' if a newer version of the product is found.
Returns 'N/A' if the product is not found.
"""

# Path to plist to read version key from [required]
Plist = '/Library/Frameworks/Adobe AIR.framework/Versions/Current/Resources/Info.plist'
# Key in plist to read version string from [required]
Key = 'CFBundleVersion'
# Version to test for [required]
Version = '21.0.0.176'
# Range limit for plist version [optional]
# Range = ['MIN', 'MAX']

# Required modules
from os import devnull
from os.path import isabs, isfile
from pkg_resources import parse_version
from re import sub
from subprocess import check_output

# Read Key's Value as String from Plist
def read_plist(p, k):
	with open(devnull, 'w') as DEVNULL:
		try:
			v = check_output(['/usr/bin/defaults', 'read', p, k], stderr=DEVNULL).rstrip()
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
	Plist
except:
	print '<result>Error: Plist path not defined</result>'
	exit(1)
try:
	Key
except:
	print '<result>Error: No Key specified</result>'
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

# Validate Plist
if (not isabs(Plist)):
	print '<result>Error: Plist path is invalid</result>'
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
if (not isfile(Plist)):
	Result = 'N/A'
else:
	Installed = read_plist(Plist, Key)
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