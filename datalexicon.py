import os
import json
import numpy

from dataiter import Dataiter

class Numeric():
	def __init__(self, fname, frange):
		self.mean = 0
		self.std = 0
		self.minimum = frange[0]
		self.maximum = frange[1]
		self.values = []
		self.outliers = [-2, -1, '']
		self.fname = fname
		self.feature_scaling = 'Standardization' 
		#'Standardization', 'Rescaling', 'MeanNormalization'

	def process_instance(self, value):
		if value not in self.outliers:
			value = float(value)
			if value < self.maximum and value > self.minimum:
				self.values.append(value)
		return

	def preprocess(self):
		nparray = numpy.array(self.values).astype(numpy.float)
		self.mean = numpy.mean(nparray)
		self.std = numpy.std(nparray)
		print(self.fname, self.mean, self.std, nparray.max(), nparray.min())
		#self.save()
	
	def save(self):
		nparray = numpy.array(self.values).astype(numpy.float)
		nparray = numpy.sort(nparray).tolist()
		cur_dir = os.getcwd()
		rel_path = 'NumericRange/' + self.fname + '.txt'
		full_path = os.path.join(cur_dir, rel_path)
		file = open(full_path, 'w')
		file.write(str(nparray))
		file.close() 

	def convert(self, value):
		#value will not be in self.outliers if we fill it with prev
		if value in self.outliers:
			value = self.mean
			#return 0.0
		value = float(value)
		if value < self.maximum*1.5 and value > self.minimum*1.5:
			if self.feature_scaling == 'Standardization':
				value = (value - self.mean)/self.std
			elif self.feature_scaling == 'Rescaling':
				value = (value - self.minimum)/(self.maximum - self.minimum)
			elif self.feature_scaling == 'MeanNormalization':
				value = (value - self.mean)/(self.maximum - self.minimum)	
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
		#and value in self.cat2index
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
					frange = self.dataiter.featureranges[fname]
					self.lexicon[fname] = Numeric(fname, frange)
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
	labeljsonfile = 'icu_label.json'
        staticjsonfile = 'icu_static.json'
        timeseriesjsonfile = 'icu_timeseries.json'
        featuresfile = 'icu_features.json'
	outliersfile = 'icu_outliers.json'

        trainfile = 'trainicuidsample.json'
        valfile = 'valicuidsample.json'
        testfile = 'testicuidsample.json'

        dataiter = Dataiter(labeljsonfile, staticjsonfile, timeseriesjsonfile, featuresfile, outliersfile, trainfile, valfile, testfile, fwindow=6, lwindow=4, gwindow=4)	
        dataiter.populatefeatures()

        lexicon = Lexicon(dataiter)
        lexicon.load()
        lexicon.create()

	print(len(lexicon.lexicon["Gender"].cat2index))

		
