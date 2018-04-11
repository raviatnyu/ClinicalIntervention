import sys
import os
import json

def fill_missing_values(source, destination):
        missing_initial = ('', -2)
        missing_middle = ('', -1)

        for line in source:
		line = line.strip().replace('\'', '\"')
		linedict = json.loads(line)
                for icu_itemid, time_series in linedict.items():
                	time_series_expand = []
                	previous_timeindex = -1
                	for value, timeindex in time_series:
                        	if timeindex <= previous_timeindex:
					print(icu_itemid, timeindex)
                                	continue
                        	while(timeindex != previous_timeindex + 1):
                                	if previous_timeindex == -1:
                                        	time_series_expand.append(missing_initial)
                                	else:
                                        	time_series_expand.append(missing_middle)
                                	previous_timeindex += 1
				previous_timeindex += 1
                        	time_series_expand.append((value,timeindex))
			destination.write('{0}\t{1}\n'.format(icu_itemid, time_series_expand))
        return

def createtimeseriesdict(icu_timeseries):
	file = open(icu_timeseries, 'r')
	return_dict = {}

        for line in file:
                line = line.strip().replace('\'', '\"')
                linedict = json.loads(line)
                for icu_itemid, time_series in linedict.items():
			stayid, itemid = icu_itemid[1:-1].split(',')
			if not stayid in return_dict:
				return_dict[stayid] = {}
			return_dict[stayid][itemid] = time_series

	return return_dict

if __name__=='__main__':
        icu_timeseries_spark = sys.argv[1]
        icu_timeseries_json = sys.argv[2]

	timeseries_dict = createtimeseriesdict(icu_timeseries_spark)
	timeseries_file = open(icu_timeseries_json, 'w')
	timeseries_file.write(json.dumps({'icustay_timeseries':timeseries_dict}))
	timeseries_file.close()
