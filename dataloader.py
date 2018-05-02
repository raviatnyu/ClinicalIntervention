import os
import torch

import torch.utils.data as data

from dataiter import Dataiter
from datalexicon import *
from dataset import Dataset


def get_data(mode='train', batch_size=2, shuffle=True, dataiter=None, lexicon=None):

	labeljsonfile = 'icu_label.json'	
        staticjsonfile = 'icu_static.json'
        timeseriesjsonfile = 'icu_timeseries.json'
        featuresfile = 'icu_features.json'
	outliersfile = 'icu_outliers.json'

        trainfile = 'trainicuidhalf.json'
        valfile = 'valicuidhalf.json'
        testfile = 'testicuidhalf.json'

	if dataiter is None:
        	dataiter = Dataiter(labeljsonfile, staticjsonfile, timeseriesjsonfile, featuresfile, outliersfile, trainfile, valfile, testfile, fwindow=6, lwindow=4, gwindow=4)
        	dataiter.populatefeatures()

	if lexicon is None:
        	lexicon = Lexicon(dataiter)
        	lexicon.load()
        	lexicon.create()

	print(len(dataiter.timeseries["icustay_timeseries"]))
        dataset = Dataset(dataiter, lexicon)
        dataset.create(mode)
	print(len(dataiter.timeseries["icustay_timeseries"]))
	dataloader = data.DataLoader(dataset, batch_size=batch_size, collate_fn=dataset.collate_fn,  shuffle=shuffle)
	
	if mode=='train': return dataloader, dataiter, lexicon, dataset.__len__()
	else: return dataloader


if __name__=='__main__':
	trainlabelsmap = {0:0, 1:0, 2:0, 3:0}
	vallabelsmap = {0:0, 1:0, 2:0, 3:0}
	testlabelsmap = {0:0, 1:0, 2:0, 3:0}
	
	trainloader, dataiter, lexicon = get_data(batch_size=128)
	for batch in trainloader:
		#print (batch[0])
		#print (batch[1])
		#print (batch[2])
		for label in batch[2]:
			trainlabelsmap[label.item()] += 1
	print(trainlabelsmap)

	valloader = get_data(mode='val', dataiter=dataiter, lexicon=lexicon, batch_size=128)
	testloader = get_data(mode='test', dataiter=dataiter, lexicon=lexicon, batch_size=128)

	for batch in valloader:
		for label in batch[2]:
			vallabelsmap[label.item()] += 1

	print(vallabelsmap)
	for batch in testloader:
		for label in batch[2]:
			testlabelsmap[label.item()] += 1
	print(testlabelsmap)

