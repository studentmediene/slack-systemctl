#!/bin/sh
# Script to check that the current user does not have
# write permission to the application (to reduce the
# consequences of a compromise).
APPLICATION_DIRS=". templates slackbot slackbot/plugins venv venv/bin"
# Iterate through the directories listed above
for d in $APPLICATION_DIRS
do
    # Check whether the directory is writable
    if test -w $d
    then
        (>&2 echo "Error: directory $d is writable by `whoami`.")
        exit 1
    fi

    # Iterate through every file in this directory
    for f in $d/*
    do
        # Check whether the file is writable
        if test -w $f
        then
            (>&2 echo "Error: file $f is writable by `whoami`.")
            exit 3
        fi
    done
done

exit 0
