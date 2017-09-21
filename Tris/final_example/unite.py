#!/usr/bin/python

import json

with open("cynical_ultimate_dataset.json") as dataset_file:
        dataset1 = json.load(dataset_file)
with open("losing_dataset.json") as dataset_file:
        dataset2 = json.load(dataset_file)
with open("cynical_ultimate_dataset.json", "w+") as outFile:
	outFile.write(json.dumps(dataset1 + dataset2))
