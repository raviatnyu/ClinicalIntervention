import os
import json
import numpy

from dataiter import Dataiter

class Numeric():
	def __init__(self, fname):
		self.mean = 0
		self.std = 0
		self.values = []
		self.outliers = [-2, -1, '']
		self.fname = fname

	def process_instance(self, value):
		if value not in self.outliers:
			self.values.append(value)
		return

	def preprocess(self):
		nparray = numpy.array(self.values).astype(numpy.float)
		self.mean = numpy.mean(nparray)
		self.std = numpy.std(nparray)
		print(self.fname, self.mean, self.std)

	def convert(self, value):
		if value not in self.outliers:
			value = (float(value) - self.mean)/self.std
		else: value = 0.0
		return value

	def clear(self):
		del self.values[:]  
		return

class Categoric():
	def __init__(self, fname):
		self.cat2index = {}
		self.index2cat = {}
		self.values = [] #counters are not needed?
		self.outliers = [-2, -1, '']
		self.fname = fname

	def process_instance(self, value):
		if value not in self.outliers:
			if value not in self.values:
				self.values.append(value)
		return

	def preprocess(self):
		for value in self.values:
			self.index2cat[len(self.cat2index)] = value
			self.cat2index[value] = len(self.cat2index)
		self.index2cat[len(self.cat2index)] = 'UNK'
		self.cat2index['UNK'] = len(self.cat2index)
		print(self.index2cat)	
		
	def convert(self, value):
		if value not in self.outliers:
			value = self.cat2index[value]
		else: value = self.cat2index['UNK']
		return value

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
					self.lexicon[fname] = Numeric(fname)
				elif ftype == "Categoric":
					self.lexicon[fname] = Categoric(fname)
			self.lexicon[fname].process_instance(fvalue)

		for icuid, fname, ftype, fvalue in self.dataiter.iterstaticdeep():
			process(fname, ftype, fvalue)
		for icuid, fname, ftype, fvalue in self.dataiter.itertimeseriesdeep():
                        process(fname, ftype, fvalue)
		return

	def create(self):
		for feature, instance in self.lexicon.items():
			instance.preprocess()
			instance.clear()
		return		

if __name__=='__main__':
        staticjsonfile = 'icu_static.json'
        timeseriesjsonfile = 'icu_timeseries.json'
        featuresfile = 'icu_features.json'

        trainfile = 'trainicuid.json'
        valfile = 'valicuid.json'
        testfile = 'testicuid.json'

        dataiter = Dataiter(staticjsonfile, timeseriesjsonfile, featuresfile, trainfile, valfile, testfile, fwindow=6, lwindow=4, gwindow=4)	
        dataiter.populatefeatures()

        lexicon = Lexicon(dataiter)
        lexicon.load()
        lexicon.create()



		
