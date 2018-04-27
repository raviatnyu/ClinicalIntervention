import os
import sys
import json

def detectoutliers(labstimeseriesfile):
	outliers = []
	labsfile = open(labstimeseriesfile, 'r')
	for line in labsfile:
		line = line.strip().replace('\'', '\"')
		line = json.loads(line)
		for key, valuelist in line.items():
			for value in valuelist:
				try: float(value[0])
				except: outliers.append(value[0])
	return list(set(outliers))

if __name__=='__main__':
	labstimeseriesfile = sys.argv[1]
	outliers = detectoutliers(labstimeseriesfile)
	print(outliers)
	print(len(outliers))

