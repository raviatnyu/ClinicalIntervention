import os

import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as functional


class MLP(nn.Module):

	def __init__(self, dict_args):
                super(MLP, self).__init__()

		self.gender_vocab_size = dict_args["gender_vocab_size"]
		self.ethnicity_vocab_size = dict_args["ethnicity_vocab_size"]
		self.admtype_vocab_size = dict_args["admtype_vocab_size"]
		self.embedding_dim = dict_args["embedding_dim"]
		self.numerical_dim = dict_args["numerical_dim"]
		self.num_steps = dict_args["num_steps"]	
		self.output_dim = dict_args["output_dim"]			
		#Dropout
		self.input_dim = self.numerical_dim*self.num_steps + 3*self.embedding_dim

		self.gender_embeddings = nn.Embedding(self.gender_vocab_size, self.embedding_dim)
		self.ethnicity_embeddings = nn.Embedding(self.ethnicity_vocab_size, self.embedding_dim)
		self.admtype_embeddings = nn.Embedding(self.admtype_vocab_size, self.embedding_dim)

		self.linear = nn.Linear(self.input_dim, self.output_dim)

	def forward(self, numericalfeatures, gfeatures, efeatures, afeatures):
		#numericalfeatures: batch_size, num_steps, num_features
		#gfeatures: batch_size
		#efeatures: batch_size
		#afeatures: batch_size

		numericalfeatures = numericalfeatures.view(numericalfeatures.size(0), -1)
		#batch_size, num_steps*num_feature
		gfeatures = self.gender_embeddings(gfeatures)
		efeatures = self.ethnicity_embeddings(efeatures)
		afeatures = self.admtype_embeddings(afeatures)
		#batch_size, emb_dim

		#print(numericalfeatures.size())
		features = torch.cat((numericalfeatures,
				      gfeatures,
				      efeatures,
				      afeatures), dim=1
				     )

		features = self.linear(features) #batch_size, output_dim

		if not self.training:
			return functional.sigmoid(features)
		#logprobs = functional.log_softmax(features, dim=1)
		return features ##batch_size, output_dim

		
if __name__=='__main__':

		dict_args = {
		                "gender_vocab_size": 2,
                		"ethnicity_vocab_size": 10, 
                		"admtype_vocab_size": 4,
                		"embedding_dim": 2,
                		"hidden_dim": 24,
                		"numerical_dim": 4,
				"num_steps": 6,
                		"output_dim": 4
			    }

		model = MLP(dict_args)
		numericalfeatures = Variable(torch.randn(2,6,4))
		gfeatures = Variable(torch.LongTensor([0,1]))
		efeatures = Variable(torch.LongTensor([4,9]))
		afeatures = Variable(torch.LongTensor([0,2]))

		logprobs = model(numericalfeatures, gfeatures, efeatures, afeatures)

		print(logprobs)
 
				
