import os
import sys
import json

def detectoutliers(labstimeseriesfile):
	outliers = {}
	outliersslim = {}
	labsfile = open(labstimeseriesfile, 'r')
	for line in labsfile:
		line = line.strip().replace('\'', '\"')
		line = json.loads(line)
		for key, valuelist in line.items():
			featurename = key[1:-1].split(',')[1]
			if featurename not in outliers:
				outliers[featurename] = []
			for value in valuelist:
				try: float(value[0])
				except: outliers[featurename].append(value[0])
	for key,valuelist in outliers.items():
		outliersslim[key] = list(set(valuelist))
	return outliers, outliersslim

if __name__=='__main__':
	labstimeseriesfile = sys.argv[1]
	outliers, outliersslim = detectoutliers(labstimeseriesfile)
	print(outliers)
	print(outliersslim)
#python outlierdetect.py icu_timeseries_labs.txt
