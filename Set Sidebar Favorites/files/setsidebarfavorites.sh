#!/bin/bash

# Author: Michael Page (21/05/15)
# Information regarding this script can be found at: http://errorfreeit.com.au/blog/2015/5/22/deploy-finders-sidebar-list-favorites

# Usage
# Install changesidebarlist.pkg: https://github.com/Error-freeIT/Change-Sidebar-List/releases/latest
# Install outset.pkg: https://github.com/chilcote/outset/releases/latest
# Copy this script into /usr/local/outset/login-once/
# Correct the scripts file permissions:
# sudo chown root:wheel /usr/local/outset && chmod -R 755 /usr/local/outset && xattr -rc /usr/local/outset

# List of intended sidebar favourites.
FAVORITES=( "/Applications" 
		"HOMEDIR/Desktop"
		"HOMEDIR/Documents"
		"HOMEDIR/Downloads"
		"HOMEDIR/Movies"
		"HOMEDIR/Music"
		"HOMEDIR/Pictures"
		"HOMEDIR" )


# Special sidebar favorites we skip removing.
IGNORED_FAVORITES=( "All My Files"
			"iCloud"
			"AirDrop" )


### Nothing below this line needs to change. ####

CHANGE_SIDEBAR_LIST_SCRIPT="/usr/local/bin/changesidebarlist"

# Create an array of current favorites.
IFS=$'\n'
CURRENT_FAVORITES=($($CHANGE_SIDEBAR_LIST_SCRIPT list | sed 's/file:.*//' | sed 's/ *$//g'))
unset IFS

# Remove all unwanted favorites apart from those in the ignored favorties array.
for CURRENT_FAVORITE in "${CURRENT_FAVORITES[@]:1}"
do

	IGNORED="false"

	# Loop through the array of ignored favorties.
	for IGNORED_FAVORITE in "${IGNORED_FAVORITES[@]}"
	do
		# If current favorite is an ignored favortie, set IGNORED to true.	
		if [[ "$IGNORED_FAVORITE" == "$CURRENT_FAVORITE" ]]
		then
			IGNORED="true"
		fi
	done

	if [[ "$IGNORED" == "false" ]]
	then
		$CHANGE_SIDEBAR_LIST_SCRIPT remove "${CURRENT_FAVORITE}"
	fi

done

# Add wanted favorites.
for FAVORITE in "${FAVORITES[@]}"
do
	$CHANGE_SIDEBAR_LIST_SCRIPT last "$FAVORITE"
done

exit 0
