#!user/bin/env python
import os
import sys
import json

import operator
import datetime

from csv import reader
from pyspark import SparkConf, SparkContext

def processtimeseries(chart_events, icu_static_dict, features_list):
	conf = SparkConf().setAppName("time series")
	sc = SparkContext(conf=conf)

	chart_events_rdd = sc.textFile(chart_events, 1)

	chart_events_rdd = chart_events_rdd.mapPartitions(lambda x: reader(x))

	def is_relevant_item(x):
		itemid = x[4]
		for feature in features_list:
			if itemid in feature["ItemIds"]:
				return True
		return False
	chart_events = chart_events_rdd.filter(is_relevant_item)

        #icu_id --> item_id, value, valuenum, charttime
        chart_events = chart_events.map(lambda x: (x[3], (x[4], x[8], x[9], x[5])))

	def replace_itemid(x):
		itemid = x[1][0]
		for feature in features_list:
			if itemid in feature["ItemIds"]:
				item = feature["Feature"]
				return (x[0], (item, x[1][1], x[1][2], x[1][3]))
		return (x[0], x[1])		
	chart_events = chart_events.map(replace_itemid)

	def is_relevant_icuid(x):
		if x[0] not in icu_static_dict.keys():
			return False
		return True
	chart_events = chart_events.groupByKey().filter(is_relevant_icuid).flatMapValues(lambda x: x)

	def timeseriesmap(x):
		def gettimeindex(starttime, curtime):
			datetimeformat = '%Y-%m-%d %H:%M:%S'
			stime = datetime.datetime.strptime(starttime, datetimeformat)
			try:
				etime = datetime.datetime.strptime(curtime, datetimeformat)
			except:
				return -1
			diff = etime - stime
			return int(diff.total_seconds()/3600)
		
		intime = icu_static_dict[x[0]]['intime']
		charttime = x[1][3]
		charttimeindex = gettimeindex(intime, charttime)	
		return ((x[0], x[1][0], charttimeindex), x[1][1])
	#icu_id, item_id, charttimeindex --> value
	chart_events = chart_events.map(timeseriesmap)

	def aggregatetimeseries(x):
		return list(x)[0]

	chart_events = chart_events.groupByKey().mapValues(aggregatetimeseries)

	#icu_id, item_id --> value, charttimeindex
	chart_events = chart_events.map(lambda x: ((x[0][0], x[0][1]), [x[1], x[0][2]]))	

	chart_events = chart_events.groupByKey().mapValues(list)	

	def sortlist(x):
		x[1].sort(key=operator.itemgetter(1))
		return (x[0], x[1])

	#icu_id, item_id --> value, charttimeindexsorted
	chart_events = chart_events.map(sortlist)	

	def expandtimeseries(x):
		missing_initial = -2
		missing_middle = -1
		time_series_expand = []
		previous_timeindex = -1
		for value, timeindex in x[1]:
			if timeindex <= previous_timeindex:
				continue
			while(timeindex != previous_timeindex + 1):
				if previous_timeindex == -1:
					time_series_expand.append([missing_initial, previous_timeindex+1])
				else:
					time_series_expand.append([missing_middle, previous_timeindex+1])
				previous_timeindex = previous_timeindex + 1
			previous_timeindex = previous_timeindex + 1
			time_series_expand.append([value,timeindex])
		return (x[0], time_series_expand)

	#icu_id, item_id --> value, charttimeindexsortedwithmissing
	chart_events = chart_events.map(expandtimeseries)

	chart_events.map(lambda x: "{0}\"({1},{2})\" : {3}{4}".format('{', x[0][0], x[0][1], x[1], '}')).saveAsTextFile("icu_timeseries.out")

	#chart_events = chart_events.map(lambda x: (x[0][0], 1)).groupByKey().mapValues(len)
	#chart_events.map(lambda x: "{0},{1}".format(x[0], x[1])).saveAsTextFile("ravi.out")

	return
	
if __name__=='__main__':
	chart_events = sys.argv[1]
	icu_static = sys.argv[2]
	#item_ids = sys.argv[3].strip().split(',')	
	features = sys.argv[3]	

	icu_static_file = open(icu_static, 'r')
	icu_static_json = json.load(icu_static_file)
	icu_static_dict = icu_static_json["icustay_static"]

	features_file = open(features, 'r')
	features_json = json.load(features_file)
	features_list = features_json["Features"]

	#processtimeseries(chart_events, icu_static_dict, item_ids)
	processtimeseries(chart_events, icu_static_dict, features_list)

#spark-submit --conf spark.pyspark.python=/share/apps/python/3.4.4/bin/python sparktimeseries.py /user/rtg267/CHARTEVENTS.csv icu_static.json icu_features.json
