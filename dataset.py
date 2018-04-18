import os
import sys

import torch
import numpy as np
import torch.utils.data as data

from dataiter import Dataiter
from datalexicon import *

class Dataset(data.Dataset):
        def __init__(self, dataiter, datalexicon):
		self.dataiter = dataiter
		self.lexicon = datalexicon
		self.numericdata = []
		self.categoricdata = []
		self.size = 0
		self.featurewindow = self.dataiter.featurewindow
		self.labelwindow = self.dataiter.labelwindow

        def __len__(self):
                return self.size

	def __getitem__(self, index):
		numeric = self.numericdata[index]
		categoric = self.categoricdata[index]
		return	[numeric, categoric]

	def getfeatureinfo(self, fname): 
		ftype, fpattern, flexicon = None, None, None
		if fname in self.dataiter.staticfeatures.keys():
			ftype = self.dataiter.staticfeatures[fname]
			fpattern = 'static'
		elif fname in self.dataiter.timeseriesfeatures.keys():
			ftype = self.dataiter.timeseriesfeatures[fname]
			fpattern = 'timeseries'
		flexicon = self.lexicon.lexicon[fname]
		if ftype == 'Numeric': findex = self.dataiter.numericfeatureindex[fname]
		elif ftype == 'Categoric': findex = self.dataiter.categoricfeatureindex[fname]
		return ftype, fpattern, flexicon, findex

	def processfeaturevalues(self, fvalues, ftype, fpattern, flexicon):
		def preprocessdata(values, lexicon):
			values = [lexicon.convert(value) for value in values]
			return values
		fvalues = preprocessdata(fvalues, flexicon)		
		if fpattern == 'static':
			staticvalue = fvalues[0]
			fvalues = [staticvalue for i in range(self.featurewindow)]
		return fvalues		

	
	def create(self):
		#change to instance, label
		for instance in self.dataiter.iterdata():
			numeric_instance_data = [None for i in range(len(self.dataiter.numericfeatureindex))]
			categoric_instance_data = [None for i in range(len(self.dataiter.categoricfeatureindex))]
			for fname, fvalues in instance.items():
				ftype, fpattern, flexicon, findex = self.getfeatureinfo(fname)
				fvalues = self.processfeaturevalues(fvalues, ftype, fpattern, flexicon)
				if ftype == 'Numeric': numeric_instance_data[findex] = fvalues
				elif ftype == 'Categoric': categoric_instance_data[findex] = fvalues
			self.numericdata.append(numeric_instance_data)
			self.categoricdata.append(categoric_instance_data)
		self.size = len(self.numericdata)
		return

	def collate_fn(self, mini_batch):
		#labelsbatch
		numericbatch, categoricbatch = zip(*mini_batch)
		numerictensor = None #batch_size*num_steps*num_numeric
		categorictensor = None #batch_size*num_steps*num_categoric
	
		for numericfeaturebatch in zip(*numericbatch):
			if numerictensor is None: numerictensor = torch.FloatTensor(numericfeaturebatch).unsqueeze(-1)
			else: numerictensor = torch.cat([numerictensor, torch.FloatTensor(numericfeaturebatch).unsqueeze(-1)], dim=2)
		
		for categoricfeaturebatch in zip(*categoricbatch):
			if categorictensor is None: categorictensor = torch.LongTensor(categoricfeaturebatch).unsqueeze(-1)
			else: categorictensor = torch.cat([categorictensor, torch.LongTensor(categoricfeaturebatch).unsqueeze(-1)], dim=2)
		return numerictensor, categorictensor
				
if __name__=='__main__':
	
        staticjsonfile = 'icu_static.json'
        timeseriesjsonfile = 'icu_timeseries.json'
        featuresfile = 'icu_features.json'

        trainfile = 'trainicuidsample.json'
        valfile = 'valicuid.json'
        testfile = 'testicuid.json'

        dataiter = Dataiter(staticjsonfile, timeseriesjsonfile, featuresfile, trainfile, valfile, testfile, fwindow=6, lwindow=4, gwindow=4)
        dataiter.populatefeatures()

        lexicon = Lexicon(dataiter)
        lexicon.load()
        lexicon.create()
		
	dataset = Dataset(dataiter, lexicon)
	dataset.create()

	print(dataset.collate_fn([dataset.__getitem__(0), dataset.__getitem__(1)]))

