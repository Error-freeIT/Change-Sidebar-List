#!/bin/bash

# Name of the package.
NAME="changesidebarlist"

# Once installed the identifier is used as the filename for a receipt files in /var/db/receipts/.
IDENTIFIER="au.com.errorfreeit.$NAME"

# Package version number.
VERSION="1.0"

# The location to copy changesidebarlist.
INSTALL_LOCATION="/usr/local/bin"

# Change into the same directory as this script.
cd "$(dirname "$0")"

# Store the path containing this script.
SCRIPT_PATH="$(pwd)"

# Ensure changesidebarlist is executable.
/bin/chmod 755 "$SCRIPT_PATH/files/changesidebarlist"

# Build the package.
/usr/bin/pkgbuild \
    --root "$SCRIPT_PATH/files/" \
    --install-location "$INSTALL_LOCATION" \
    --identifier "$IDENTIFIER" \
    --version "$VERSION" \
    "$SCRIPT_PATH/package/$NAME-$VERSION.pkg"