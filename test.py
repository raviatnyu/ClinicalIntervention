import os
import sys
import json
import pickle

import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as functional
import torch.optim as optim

import dataloader as loader
import evaluate as evaluator

from modelmlp import MLP

if torch.cuda.is_available(): USE_CUDA = True
else: USE_CUDA = False

def test(modelname, modelfilename):
	modeldict = open(os.path.join('models/', modelfilename), 'rb')
	checkpoint = torch.load(modeldict)
	dict_args = checkpoint['dict_args']
	if modelname == 'mlp':
		model = MLP(dict_args)
	model.load_state_dict(checkpoint['state_dict'])
	if USE_CUDA:
		model = model.cuda()

	test_batch_size = 200
	testloader, dataiter, lexicon, test_data_size = loader.get_data(batch_size=test_batch_size)

	return evaluator.evaluate(model, testloader, dataiter)

if __name__=='__main__':
	epoch = sys.argv[1]
	modelname = 'mlp'
	modelfilename = 'MLP/epoch' + epoch + '/' + modelname + '.pth'
	print(modelfilename)
	print(test(modelname, modelfilename))

	

