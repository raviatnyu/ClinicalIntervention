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

import numpy
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score

import dataloader as loader

from modelmlp import MLP
#from modelrecurrent import Recurrent

if torch.cuda.is_available(): USE_CUDA = True
else: USE_CUDA = False


def evaluate(model, valloader, dataiter):
        num_correct, num_total, bayes_acc = 0.0, 0.0, 0.0
	ypredictions, ytargets, yscores = [], [], []
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
                        probs = model(numericalfeatures, gfeatures, efeatures, afeatures)
                        #predictions = probs.max(dim=-1)[1]
			predictions = (probs > 0.5).long().view(-1)
                        bayes_acc = bayes_acc + (labels==0).sum().item()
                        num_correct = num_correct + (predictions==labels).sum().item()
                        num_total = num_total + batch_size
			ypredictions.extend(predictions.cpu().data.numpy().tolist())
			ytargets.extend(labels.cpu().data.numpy().tolist())
			yscores.extend(probs.view(-1).cpu().data.numpy().tolist())

	print(ypredictions[0:20])
	print(ytargets[0:20])
	print(yscores[0:20])
	auc = roc_auc_score(ytargets, yscores)
	tn, fp, fn, tp = confusion_matrix(ytargets, ypredictions).ravel()
	accuracy = (tp+tn+0.0)/(tp+tn+fp+fn+0.0)
	recall = tp/(tp+fn+0.0)
	print("TP", tp)
	print("FP", fp)
	print("FN", fn)
	print("TN", tn)
	print(accuracy)
	print(len(ypredictions))
	print(len(ytargets))
	print("AUC", auc)
	del ypredictions[:]
	del ytargets[:]
	del yscores[:]
        return num_correct/num_total, bayes_acc/num_total, accuracy, recall, auc

