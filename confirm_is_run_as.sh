#!/bin/sh
if test `whoami` != "$1"
then (>&2 echo "Error: The application must be run as $1, not `whoami`")
     exit 1
else exit 0
fi
