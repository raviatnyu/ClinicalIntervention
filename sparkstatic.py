#!user/bin/env python
import os
import sys

from csv import reader
from pyspark import SparkConf, SparkContext
import datetime

def processstatic(icu_stays, admissions, patients):
	conf = SparkConf().setAppName("static")
	sc = SparkContext(conf=conf)

	icu_stays_rdd = sc.textFile(icu_stays, 1)
	admissions_rdd = sc.textFile(admissions, 1)
	patients_rdd = sc.textFile(patients, 1)

	icu_stays_rdd = icu_stays_rdd.mapPartitions(lambda x: reader(x))
	admissions_rdd = admissions_rdd.mapPartitions(lambda x: reader(x))
	patients_rdd = patients_rdd.mapPartitions(lambda x: reader(x))
	
	#hadm_id --> patient_id, icustay_id, intime, outtime
	icu_stays = icu_stays_rdd.map(lambda x: (x[2], (x[1], x[3], x[9], x[10])))
	#hadm_id --> patient_id, adm_type, ethnicity
	admissions = admissions_rdd.map(lambda x: (x[2], (x[1], x[6], x[13])))
	
	icu_adm = icu_stays.join(admissions)

	#icustay_id --> patient_id, patient_id, adm_type, ethnicity, intime, outtime
	#icu_adm = icu_adm.map(lambda x: (x[1][0][1] , (x[1][0][0], x[1][1][0], x[1][1][1], x[1][1][2], x[1][0][2], x[1][0][3])))
	#icu_adm = icu_adm.filter(lambda x: x[1][0] == x[1][1])

	#patient_id --> icustay_id, adm_type, ethnicity, intime, outtime, hadmid
	icu_adm = icu_adm.map(lambda x: (x[1][0][0] , (x[1][0][1], x[1][1][1], x[1][1][2], x[1][0][2], x[1][0][3], x[0])))
	#patient_id --> gender, dateofb
	patients = patients_rdd.map(lambda x : (x[1], (x[2], x[3])))

	icu_adm = icu_adm.join(patients)

	def datetime_diff(stime, etime, units, default):
		datetimeformat = '%Y-%m-%d %H:%M:%S'
		try:
			stime = datetime.datetime.strptime(stime, datetimeformat)
			etime = datetime.datetime.strptime(etime, datetimeformat)
		except:
			return default
		diff = etime - stime
		if units == 'years':
			return int(diff.days/365)
		elif units == 'hours':
			return diff.total_seconds()/3600

	#icustay_id --> patient_id, adm_type, ethnicity, intime, outtime, gender, dateofb, age, hadm_id
	icu_adm = icu_adm.map(lambda x: (x[1][0][0], (x[0], x[1][0][1], x[1][0][2], x[1][0][3], x[1][0][4], x[1][1][0], x[1][1][1], datetime_diff(x[1][1][1], x[1][0][3], 'years', 500), x[1][0][5])))

	def filterpatients(x):
		age = int(x[1][7])
		if age > 99 or age < 15:
			return False
		staylength = datetime_diff(x[1][3], x[1][4], 'hours', -1)
		if staylength < 12 or staylength > 240:
			return False 
		return True
			
	icu_adm = icu_adm.filter(filterpatients)	

	icu_adm.map(lambda x: "{0}\t{1},{2},{3},{4},{5},{6},{7},{8},{9}".format(x[0], x[1][0], x[1][1], x[1][2], x[1][3], x[1][4], x[1][5], x[1][6], x[1][7], x[1][8])).saveAsTextFile("icu_static.out")

	return
	
if __name__=='__main__':
	icu_stays = sys.argv[1]
	admissions = sys.argv[2]
	patients = sys.argv[3]

	processstatic(icu_stays, admissions, patients)

	#spark-submit --conf spark.pyspark.python=/share/apps/python/3.4.4/bin/python sparkstatic.py /user/rtg267/ICUSTAYS.csv /user/rtg267/ADMISSIONS.csv /user/rtg267/PATIENTS.csv
