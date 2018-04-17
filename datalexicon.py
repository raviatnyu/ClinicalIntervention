import os
import json

from dataiter import Dataiter

class Numeric():
	def __init__(self):
		self.mean = 0
		self.std = 0
		self.values = []
		self.outliers = [-2, -1, '']

	def process_instance(self, value):
		if value not in self.outliers:
			self.values.append(value)
		return

	def preprocess(self):
		print(len(self.values))
	
	def convert(self):
		#Handle null value as well as missing value replacement

	def clear(self):
		del self.values[:]  
		return

class Categoric():
	def __init__(self):
		self.cat2index = {}
		self.index2cat = {}
		self.values = [] #counters are not needed?
		self.outliers = [-2, -1, '']
	
	def process_instance(self, value):
		if value not in self.outliers:
			if value not in self.values:
				self.values.append(value)
		return

	def preprocess(self):
		print(len(self.values))

	def convert(self):
		#Handle null value as well as missing value replacement

	def clear(self):
		del self.values[:] 
		return


class Lexicon():

	def __init__(self, dataiter):
		self.dataiter = dataiter
		self.lexicon = {} #feature, object

	def load(self):
		def process(fname, ftype, fvalue):
			if fname not in self.lexicon:
				if ftype == "Numeric":
					self.lexicon[fname] = Numeric()
				elif ftype == "Categoric":
					self.lexicon[fname] = Categoric()
			self.lexicon[fname].process_instance(fvalue)

		for icuid, fname, ftype, fvalue in self.dataiter.iterstaticdeep():
			process(fname, ftype, fvalue)
		for icuid, fname, ftype, fvalue in self.dataiter.itertimeseriesdeep():
                        process(fname, ftype, fvalue)
		return

	def create(self):
		for feature, instance in self.lexicon.items():
			instance.preprocess()
		return		

if __name__=='__main__':
        staticjsonfile = 'icu_static.json'
        timeseriesjsonfile = 'icu_timeseries.json'
        featuresfile = 'icu_features.json'

        dataiter = Dataiter(staticjsonfile, timeseriesjsonfile, featuresfile)
        dataiter.populatefeatures()

	lexicon = Lexicon(dataiter)
	lexicon.load()
	lexicon.create()



		
