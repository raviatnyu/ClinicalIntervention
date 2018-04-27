import os
import sys
import json


def createstaticdict(icu_static):
	file = open(icu_static, 'r')
	return_dict = {}
	for icu_stay in file:
		stayid, attributes = icu_stay.strip().split('\t')
		patient_id, adm_type, ethnicity, intime, outtime, \
			gender, dateofb, age, hadm_id = attributes.split(',')
		return_dict[stayid] = {
					 'PatientId': patient_id,
					 'AdmissionType': adm_type,
					 'Ethnicity': ethnicity,
					 'Intime': intime,
					 'Outtime': outtime,
					 'Gender': gender,
					 'Dateofbirth': dateofb,
					 'Age': age,
					 'HadmId': hadm_id
					}
	return return_dict

if __name__=='__main__':
	icu_static_spark = sys.argv[1]
	icu_static_json = sys.argv[2]
	static_dict = createstaticdict(icu_static_spark)
	static_file = open(icu_static_json, 'w')
	static_file.write(json.dumps({'icustay_static':static_dict}))
	static_file.close()
