#!/usr/bin/python

"""
Determines if the Adobe Gaming SDK is at least a specified Version by searching for bundles with a specific CFBundleIdentifier and reading the VersionInfo.txt in the bundle's parent folder.
Version infotmation is read from a text file (VersionInfo.txt) in the bundle's parent directory.
Results may (optionally) be limited to a range, when the CFBundleIdentifier is used for multiple major releases of the product.
A default path for the bundle may (optionally) be explicitly specified to check.
Returns 'Older' if an older version of the product is found.
Returns 'Equal' if the same version of a product is found.
Returns 'Newer' if a newer version of the product is found.
Returns 'N/A' if the product is not found.
"""

# CFBundleIdentifier to search for [required]
CFBundleIdentifier = 'com.apple.ScriptEditor.id.Install-AwayBuilder'
# Version to test for [required]
Version = '1.2.172'
# Range limit for bundle version [optional]
Range = ['1.2', '1.3']
# Default path for bundle [recommended]
Default = '/Applications/Adobe Gaming SDK 1.2'

# Required modules
from os import devnull
from os.path import dirname, exists, isabs, isfile
from pkg_resources import parse_version
from re import sub
from subprocess import check_output

# Read Version from VersionInfo text file
def read_versioninfo(f):
	v = open(f).read().splitlines()[0]
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

# Initialise array for Folders
Folders = []
# Test Default path, add bundle to array if it exists
if (Default):
	if (exists(Default)): Folders.append(Default)
# Search for bundles and add parent folder to array
for Bundle in find_bundles(CFBundleIdentifier):
	if (not dirname(Bundle) in Folders): Folders.append(dirname(Bundle))

# If we have no results check Spotlight status
if (len(Folders) == 0):
	mdStatus = check_output(['/usr/bin/mdutil', '-s', '/'])
	# If Spotlight is disabled exit here to avoid a false result
	if 'disabled' in mdStatus:
		print '<result>Error: Spotlight is disabled</result>'
		exit(1)
	else:
		print '<result>N/A</result>'
		exit(0)
else:
	# Initialise array for VersionInfo files
	VersionInfo = []
	# Check default location for VersionInfo file in folder(s)
	for Folder in Folders:
		if (isfile(Folder + '/VersionInfo.txt')):
			VersionInfo.append(Folder + '/VersionInfo.txt')
	# If no VersionInfo file(s), exit here
	if (len(Plists) == 0):
		print '<result>Error: VersionInfo.txt not in folder(s)</result>'
		exit(1)
	else:
		# Initialise array for Results
		Results = []
		# Check version in VersionInfo file(s)
		for i, File in enumerate(VersionInfo):
			# Read version from VersionInfo
			Installed = read_versioninfo(File)
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