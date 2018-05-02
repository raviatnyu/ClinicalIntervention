import os
import sys
import json
import pickle
import time

import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as functional
import torch.optim as optim

import dataloader as loader
from evaluate import evaluate
from modelmlp import MLP
#from modelrecurrent import Recurrent

if torch.cuda.is_available(): USE_CUDA = True
else: USE_CUDA = False

'''def evaluate(model, valloader, dataiter):
	num_correct = 0.0
	num_total = 0.0
	bayes_acc = 0.0
	if True:
		for i,batch in enumerate(valloader):
                        numericalfeatures = batch[0] #batch_size, num_steps, num_features
                        categoricalfeatures = batch[1] #batch_size, num_steps, num_features
                        labels = batch[2] #batch_size
			batch_size = len(labels)

                        categoricalfeatures = categoricalfeatures.permute(2,1,0)
                        gfeatures = categoricalfeatures[dataiter.categoricfeatureindex["Gender"]][0]
                        efeatures = categoricalfeatures[dataiter.categoricfeatureindex["Ethnicity"]][0]
                        afeatures = categoricalfeatures[dataiter.categoricfeatureindex["AdmissionType"]][0]
                        #######Load Data
                        if USE_CUDA:
                                numericalfeatures = numericalfeatures.cuda()
                                gfeatures = gfeatures.cuda()
                                efeatures = efeatures.cuda()
                                afeatures = afeatures.cuda()
				labels = labels.cuda()
                        model = model.eval()
                        logprobs = model(numericalfeatures, gfeatures, efeatures, afeatures)
			predictions = logprobs.max(dim=-1)[1]
			bayes_acc = bayes_acc + (labels==0).sum().item()
			num_correct = num_correct + (predictions==labels).sum().item()
			num_total = num_total + batch_size
	return num_correct/num_total, bayes_acc/num_total'''

def train():
	cur_dir = os.getcwd()
	save_dir, modeltype = 'models/MLP', 'mlp'
	save_dir_path = os.path.join(cur_dir, save_dir)
	if not os.path.exists(save_dir_path):
		os.makedirs(save_dir_path)
	print(save_dir)

	train_batch_size = 200
	val_batch_size = 200
	trainloader, dataiter, lexicon, train_data_size = loader.get_data(batch_size=train_batch_size)
	valloader = loader.get_data(mode='val', dataiter=dataiter, lexicon=lexicon, batch_size=val_batch_size)

	lexiconfile = open(os.path.join(save_dir, 'lexicon.pkl'), 'wb')
	pickle.dump(lexicon, lexiconfile)
	lexiconfile.close()
	
	dict_args = {
                                "gender_vocab_size": len(lexicon.lexicon["Gender"].cat2index),
                                "ethnicity_vocab_size": len(lexicon.lexicon["Ethnicity"].cat2index),
                                "admtype_vocab_size": len(lexicon.lexicon["AdmissionType"].cat2index),
                                "embedding_dim": 3,
                                "hidden_dim": 200,
                                "numerical_dim": 18,
                                "num_steps": 6,
                                "output_dim": 1
		    }
	
	model = MLP(dict_args)
	print(dict_args)

	learning_rate = 1
	#criterion = nn.NLLLoss()
	#criterion = nn.CrossEntropyLoss()
	criterion = nn.BCEWithLogitsLoss()
	optimizer = optim.Adadelta(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate, rho=0.9, eps=1e-06, weight_decay=0)
	#learning_rate = 0.1
	#optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, weight_decay=0.1)	

	if USE_CUDA:
		model = model.cuda()
		criterion = criterion.cuda()

	print("Start training...")
	num_epochs = 10
	for epoch in range(num_epochs):

		start_time = time.time()
		for i,batch in enumerate(trainloader):
			numericalfeatures = batch[0] #batch_size, num_steps, num_features
			categoricalfeatures = batch[1] #batch_size, num_steps, num_features
			labels = batch[2] #batch_size
			
			categoricalfeatures = categoricalfeatures.permute(2,1,0)
			gfeatures = categoricalfeatures[dataiter.categoricfeatureindex["Gender"]][0]
			efeatures = categoricalfeatures[dataiter.categoricfeatureindex["Ethnicity"]][0]
			afeatures = categoricalfeatures[dataiter.categoricfeatureindex["AdmissionType"]][0]

			load_time =  time.time()
			#######Load Data
			if USE_CUDA:
				numericalfeatures = numericalfeatures.cuda()
				gfeatures = gfeatures.cuda()
				efeatures = efeatures.cuda()
				afeatures = afeatures.cuda()
				labels = labels.cuda()
			cuda_time = time.time()

			#######Forward
			model = model.train()
			optimizer.zero_grad()
			logprobs = model(numericalfeatures, gfeatures, efeatures, afeatures)
			model_time = time.time()

			loss = criterion(logprobs.squeeze(), labels.float())

			loss_time = time.time()

			#######Backward
			loss.backward(retain_graph=False)
			optimizer.step()

			opt_time = time.time()

			#######Report
			if((i+1)%50== 0):
				accuracy, bayes, _, _ ,_ = evaluate(model, valloader, dataiter)
				print("Accuracy : ", accuracy, bayes)
				#torch.cuda.empty_cache()
				print('Epoch: [{0}/{1}], Step: [{2}/{3}], Test Loss: {4}'.format( \
							epoch+1, num_epochs, i+1, train_data_size//train_batch_size, loss.data[0]))

				if not os.path.isdir(os.path.join(save_dir, "epoch{}_{}".format(epoch,i))):
                                	os.makedirs(os.path.join(save_dir, "epoch{}_{}".format(epoch,i)))
                        	filename = modeltype + '.pth'
                        	file = open(os.path.join(save_dir, "epoch{}_{}".format(epoch,i), filename), 'wb')
                        	torch.save({'state_dict':model.state_dict(), 'dict_args':dict_args}, file)
                        	print('Saving the model to {}'.format(save_dir+"epoch{}_{}".format(epoch,i)))
                        	file.close()

			#print("Load : {0}, Cuda : {1}, Model : {2}, Loss : {3}, Opt : {4}".format(start_time-load_time, load_time - cuda_time, cuda_time - model_time, model_time - loss_time, loss_time-opt_time))
			start_time = time.time()

		'''if(epoch%1 == 0): #After how many epochs
			accuracy, bayes, _, _, _ = evaluate(model, valloader, dataiter)
			print("Accuracy : ", accuracy, bayes)
			if not os.path.isdir(os.path.join(save_dir, "epoch{}".format(epoch))):
				os.makedirs(os.path.join(save_dir, "epoch{}".format(epoch)))
			filename = modeltype + '.pth'
			file = open(os.path.join(save_dir, "epoch{}".format(epoch), filename), 'wb')
			torch.save({'state_dict':model.state_dict(), 'dict_args':dict_args}, file)
			print('Saving the model to {}'.format(save_dir+"epoch{}".format(epoch)))
			file.close()'''

if __name__=='__main__':
	train()
