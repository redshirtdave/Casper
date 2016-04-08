#!/bin/bash

# Split all supplied Parameters into an array
Parameters=( "$@" )

# Begin cycling through the Parameters array from index 3 and execute each trigger
i=3
while [ ${i} -lt ${#Parameters[@]} ]
do
    if [ -n "${Parameters[i]}" ]
    then
    	jamf policy -trigger "${Parameters[i]}"
    fi
	let i++
done

exit 0
