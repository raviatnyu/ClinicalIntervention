import os
import sys
import json
import datetime

def createlabeldict(icu_static, label_durations_file):
	def gettimeindex(starttime, curtime):
		datetimeformat = '%Y-%m-%d %H:%M:%S'
		stime = datetime.datetime.strptime(starttime, datetimeformat)
		try:
			etime = datetime.datetime.strptime(curtime, datetimeformat)
		except:
			return -1
		diff = etime - stime
		return int(diff.total_seconds()/3600)

	label_durations = open(label_durations_file, 'r')
	label_dict = {}
	for instance in label_durations:
		stayid, staynum, starttime, endtime, duration = instance.split(',')
		if stayid in icu_static:
			if stayid not in label_dict:
				label_dict[stayid] = [[0,-1]]
			intime = icu_static[stayid]['Intime']
			starttimeindex = gettimeindex(intime, starttime)
			endtimeindex = gettimeindex(intime, endtime)
			prevtimeindex = label_dict[stayid][-1][1]
			off = [[0,i+prevtimeindex+1] for i in range(starttimeindex-prevtimeindex-1)]
			on = [[1, i+starttimeindex] for i in range(endtimeindex-starttimeindex+1)]
			label_dict[stayid].extend(off)
			label_dict[stayid].extend(on)
	print(len(label_dict.keys()))
	for stayid in icu_static.keys():
		if stayid not in label_dict:
			label_dict[stayid] = [[0,-1], [0,0], [0,1]]
	for stayid in label_dict.keys():
		i = 0
		for value,tindex in label_dict[stayid]:
			if tindex < 0: i = i + 1
			else: break
		label_dict[stayid] = label_dict[stayid][i:]
	print(len(icu_static.keys()))
	print(len(label_dict.keys()))
	return label_dict

if __name__=='__main__':
	icu_label_json = sys.argv[3]
	label_durations_file = sys.argv[2]
	icu_static_json = sys.argv[1]
	icu_static_dict = json.load(open(icu_static_json, 'r'))
	icu_static = icu_static_dict["icustay_static"]
	label_dict = createlabeldict(icu_static, label_durations_file)
        label_file = open(icu_label_json, 'w')
        label_file.write(json.dumps({'icustay_label':label_dict}))
        label_file.close()
#python jsonlabel.py icu_static.json ventdurations.csv icu_label.json
