import sys
import os
import json


def createtimeseriesdict(icu_timeseries_vitals, icu_timeseries_labs):
	vitalsfile = open(icu_timeseries_vitals, 'r')
	labsfile = open(icu_timeseries_labs, 'r')
	return_dict = {}

	def populate_dict(file, addicukey=False):
        	for line in file:
                	line = line.strip().replace('\'', '\"')
                	linedict = json.loads(line)
                	for icu_itemid, time_series in linedict.items():
				stayid, itemid = icu_itemid[1:-1].split(',')
				if not stayid in return_dict:
					if not addicukey: continue
					return_dict[stayid] = {}
				return_dict[stayid][itemid] = time_series

	populate_dict(vitalsfile, addicukey = True)
	populate_dict(labsfile, addicukey = False)
	vitalsfile.close()
	labsfile.close()
	return return_dict

if __name__=='__main__':
	icu_timeseries_vitals_spark = sys.argv[1]
	icu_timeseries_labs_spark = sys.argv[2]
        icu_timeseries_json = sys.argv[3]

	timeseries_dict = createtimeseriesdict(icu_timeseries_vitals_spark, icu_timeseries_labs_spark)
	timeseries_file = open(icu_timeseries_json, 'w')
	timeseries_file.write(json.dumps({'icustay_timeseries':timeseries_dict}))
	timeseries_file.close()
