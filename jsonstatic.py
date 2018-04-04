import os
import sys
import json


def createstaticdict(icu_static):
	file = open(icu_static, 'r')
	return_dict = {}
	for icu_stay in file:
		stayid, attributes = icu_stay.strip().split('\t')
		patient_id, adm_type, ethnicity, intime, outtime, \
			gender, dateofb, age = attributes.split(',')
		return_dict[stayid] = {
					 'patient_id': patient_id,
					 'adm_type': adm_type,
					 'ethnicity': ethnicity,
					 'intime': intime,
					 'outtime': outtime,
					 'gender': gender,
					 'dateofb': dateofb,
					 'age': age
					}
	return return_dict

if __name__=='__main__':
	icu_static_spark = sys.argv[1]
	icu_static_json = sys.argv[2]
	static_dict = createstaticdict(icu_static_spark)
	static_file = open(icu_static_json, 'w')
	static_file.write(json.dumps({'icustay_static':static_dict}))
	static_file.close()
