#!/usr/bin/env bash

# A script to copy the essential data from the remote Heroku
# database to a local dev database. We don't dump things
# like ContentTypes because they seem to cause problems when loaded.
# We dump to multiple fixtures to fix foreign key dependency
# issues.
#
# Beware: this destroys the current local database.
#
# This script occasionally fails: Heroku's dumpdata output is
# cut off and loading will raise a DeserializationError. I'm not
# sure if the script is timing out or something else; running it
# again, or running each piece manually, seems to resolve it.

temp=temp
mkdir temp

core=$temp/core.json
users=$temp/users.json
trips=$temp/trips.json
people=$temp/people.json
fixtures="$core $users $trips $people"

function dump {
    echo "Dumping $1 to $2"
    heroku run manage dumpdata --indent 4 $1 > $2
}

dump 'users' $users
dump 'db permissions timetable' $core
dump 'transport trips croos' $trips
dump 'applications incoming safety raids' $people

# make db backup?
manage=./manage.py
$manage sqlflush | $manage dbshell
$manage loaddata $fixtures
