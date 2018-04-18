import os
import numpy
import json

def createsplit(static_data, splitratio, trainfile, valfile, testfile):
	icu_ids = list(static_data.keys())
	numpy.random.shuffle(icu_ids)
	train_end = int(len(icu_ids)*splitratio[0])
	val_end = int(len(icu_ids)*(splitratio[0]+splitratio[1]))
	train_ids = icu_ids[:train_end]
	val_ids = icu_ids[train_end:val_end]
	test_ids = icu_ids[val_end:]
	print(len(train_ids))
	print(len(val_ids))
	print(len(test_ids))
	
	def writejson(filename, ids):
		file = open(filename, 'w')
		file.write(json.dumps({'IcuIds':ids}))
		file.close()

	writejson(trainfile, train_ids)
	writejson(valfile, val_ids)
	writejson(testfile, test_ids)	
	return

if __name__=='__main__':

	staticjsonfile = 'icu_static.json'
	trainfile = 'trainicuid.json'
	valfile = 'valicuid.json'
	testfile = 'testicuid.json'
	splitratio = [0.7, 0.15, 0.15] #train, val, test
	
	static = json.load(open(staticjsonfile, 'r'))
	static_data = static["icustay_static"]
	
	createsplit(static_data, splitratio, trainfile, valfile, testfile)
