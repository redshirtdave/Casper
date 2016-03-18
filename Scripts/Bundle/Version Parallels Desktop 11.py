#!/usr/bin/python

"""
Determines if a product is at least a specified Version by searching for bundles with a specific CFBundleIdentifier and Version.
The Key in the product bundle's Info.plist file may be specified to obtain the product's version.
Typically the Key is 'CFBundleShortVersionString' or 'CFBundleVersion', although a custom Key may be specified.
Results may (optionally) be limited to a range, when the CFBundleIdentifier is used for multiple major releases of the product.
A default path for the bundle may (optionally) be explicitly specified to check. Recommended as a fallback when Spotlight is disabled.
Returns 'Older' if an older version of the product is found.
Returns 'Equal' if the same version of a product is found.
Returns 'Newer' if a newer version of the product is found.
Returns 'N/A' if the product is not found.
"""

# CFBundleIdentifier to search for [required]
CFBundleIdentifier = 'com.parallels.desktop.console'
# Key in plist to read version string from [required]
Key = 'CFBundleShortVersionString'
# Version to test for [required]
Version = '11.1.2'
# Range limit for bundle version [optional]
Range = ['11', '12']
# Default path for bundle [recommended]
Default = '/Applications/Parallels Desktop.app'

# Required modules
from os import devnull
from os.path import exists, isabs, isfile
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

# Find Bundles with identifier
def find_bundles(id):
	r = check_output(['/usr/bin/mdfind', 'kMDItemCFBundleIdentifier', '=', '"' + id + '"']).strip().split('\n')
	r = filter(lambda a: a != '', r)
	return r

# Initialise variables
try:
	CFBundleIdentifier
except:
	print '<result>Error: CFBundleIdentifier not defined</result>'
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
try:
	Default
except:
	Default = None


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

# Validate Default
if (Default):
	if (not isabs(Default)):
		print '<result>Error: Default path is invalid</result>'
		exit(1)

# Initialise array for Bundles
Bundles = []
# Test Default path, add bundle to array if it exists
if (Default):
	if (exists(Default)): Bundles.append(Default)
# Search for bundles and add to array
for Bundle in find_bundles(CFBundleIdentifier):
	if (not Bundle in Bundles): Bundles.append(Bundle)

# If we have no results check Spotlight status
if (len(Bundles) == 0):
	mdStatus = check_output(['/usr/bin/mdutil', '-s', '/'])
	# If Spotlight is disabled exit here to avoid a false result
	if 'disabled' in mdStatus:
		print '<result>Error: Spotlight is disabled</result>'
		exit(1)
	else:
		print '<result>N/A</result>'
		exit(0)
else:
	# Initialise array for Plists
	Plists = []
	# Check default location(s) for plist in bundle(s)
	for Bundle in Bundles:
		if (isfile(Bundle + '/Contents/Info.plist')):
			Plists.append(Bundle + '/Contents/Info.plist')
		elif (isfile(Bundle + '/Resources/Info.plist')):
			Plists.append(Bundle + '/Resources/Info.plist')
	# If no plist(s), exit here
	if (len(Plists) == 0):
		print '<result>Error: Info.plist not in bundle(s)</result>'
		exit(1)
	else:
		# Initialise array for Results
		Results = []
		# Check version in plist(s)
		for i, Plist in enumerate(Plists):
			# Read version from key in plist
			Installed = read_plist(Plist, Key)
			# Rationalise the version string for comparison
			Installed = rationalise_version(Installed)
			if (Installed == ''):
				# If we get an empty string for the version add error message
				Results.append('Error: Reading installed version')
			else:
				# Compare our versions and append to array
				Results.append(compare_versions(Installed, Version))
				if (Range):
					# If the installed version is outside of the range, update the entry in the array
					if (version_in_range(Installed, Range) == False):
						Results[i] = 'N/A'

		# Prioritise our results
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

		# Output final result
		print '<result>' + Result + '</result>'
		exit(0)