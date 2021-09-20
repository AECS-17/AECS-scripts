#!/usr/bin/env python
# Copyright 2021 Frédéric Wang. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import argparse, re, sys, urllib.request

FRAMADATE_SERVER = "https://framadate.org"
INSCRITS="Inscrits"
ENCADRANTS="Encadrants"

# Parse the arguments.
parser = argparse.ArgumentParser()
parser.add_argument("url",
                    help="Public link to the framadate poll")
args = parser.parse_args()

# Download the CSV file.
result = re.match("^%s/([a-zA-Z0-9]+)$" % FRAMADATE_SERVER, args.url)
if result is None:
    sys.exit("invalid framadate url")
framadate_hash = result.group(1)
response = urllib.request.urlopen("%s/exportcsv.php?poll=%s" %
                                  (FRAMADATE_SERVER, framadate_hash))
data = response.readlines()

# Parse the day title.
day_title = data.pop(0).decode('utf-8').strip(",\n\r").split(",")
day_count = min(7, len(day_title))

day_people = []
for title in day_title:
    day_people.append({
        INSCRITS: [],
        ENCADRANTS: [],
    })

# Parse the people.
subset = INSCRITS
for line in data:
    line = line.decode('utf-8').rstrip("\n\r").split(",")
    name = line.pop(0).strip('\"')
    if name[0] == "_":
        assert subset == INSCRITS
        subset = ENCADRANTS
        continue
    for i in range(0, day_count):
        reply = line[i].strip('\"')
        if (reply in ["Yes", "Oui"]):
            day_people[i][subset].append(name)
        elif (subset == INSCRITS and
              reply in ["Si nécessaire", "Under reserve"]):
            day_people[i][subset].append(name + "?")

# Helper function to print a list of people.
def formatPeopleList(people):
    if len(people) == 0:
        return "N/A"
    s = ""
    sorted_people = sorted(people)
    for i in range(0, len(sorted_people)):
        if i > 0:
            s += ", "
        s += sorted_people[i]
    return s

# Print the agenda.
print("Programme de la semaine :\n")
for i in range(0, day_count):
    print(day_title[i])
    for subset in day_people[i]:
        print(subset, ":", formatPeopleList(day_people[i][subset]))
    print()
