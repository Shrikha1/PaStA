#!/bin/bash

# Copyright (c) OTH Regensburg, 2017-2020
#
# Author:
#   Ralf Ramsauer <ralf.ramsauer@othr.de>
#
# This work is licensed under the terms of the GNU GPL, version 2.  See
# the COPYING file in the top-level directory.

ARCHIVE_TYPE=$1
LISTNAME=$2
BASEDIR=$3
TMP=$(mktemp)

# Remove last character (\n) from the input and store the file
head -c -1 /dev/stdin > $TMP
./process_mail.sh $ARCHIVE_TYPE $LISTNAME $BASEDIR $TMP
RET=$?

if [ $RET -eq 0 ]; then
	rm $TMP
fi
exit $RET
