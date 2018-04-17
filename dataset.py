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
		self.data = []
		self.size = 0
		self.featurewindow = self.dataiter.featurewindow
		self.labelwindow = self.dataiter.labelwindow

        def __len__(self):
                return self.size

	def __getitem__(self, index):
		#concatenate time series and statis features
		return	self.data[index]

	def getfeatureinfo(self, fname): 
		ftype, fpattern, flexicon = None, None, None
		if fname in self.dataiter.staticfeatures.keys():
			ftype = self.dataiter.staticfeatures[fname]
			fpattern = 'static'
		elif fname in self.dataiter.timeseriesfeatures.keys():
			ftype = self.dataiter.timeseriesfeatures[fname]
			fpattern = 'timeseries'
		flexicon = self.lexicon[fname]
		findex = self.dataiter.featureindex[fname]
		return ftype, fpattern, flexicon, findex

	def processfeaturevalues(self, fvalues, ftype, fpattern, flexicon):
		def preprocessdata(values, lexicon):
			values = [lexicon.convert(value) for value in values]
		fvalues = preprocessdata(fvalues, flexicon)		
		if fpattern == 'static':
			staticvalue = fvalues[0]
			fvalues = [staticvalue for i in range(self.featurewindow)]
		return fvalues		

	def create(self):
		for instance in self.dataiter.iterdata():
			instance_data = [None for i in range(len(self.dataiter.featureindex))]
			for fname, fvalues in instance.items():
				ftype, fpattern, flexicon, findex = self.getfeatureinfo(fname)
				fvalues = processfeaturevalues(fvalues, ftype, fpattern, flexicon)
				instance_data[findex] = fvalues
			self.data.append(instance_data)
		return
						

		




