#!/usr/bin/python
# -*- coding: utf-8 -*-

import torch
from torch.autograd import Variable
from random import randint
import json
import pprint

import torch.utils.data as data_utils


# Load dataset
with open("rotate_cynical_dataset.json") as dataset_file:
	dataset = json.load(dataset_file)

# N is dataset size; D_in is input dimension;
# H is hidden dimension; D_out is output dimension.
N, D_in, H, D_out = len(dataset), 27, 56, 1

epoch_num = 10
batch_size = 64
learning_rate = 0.003

x = []
y = []

for i in range(N):
	x.append(dataset[i]["state"])
	y.append(dataset[i]["result"])

x = torch.Tensor(x)
y = torch.Tensor(y)

# DataLoader
train = data_utils.TensorDataset(x, y)
train_loader = data_utils.DataLoader(train, batch_size=batch_size, shuffle=True)

# Use the nn package to define our model and loss function.
try:
	model = torch.load("trained_model")

except:
	model = torch.nn.Sequential(
		torch.nn.Linear(D_in, H),
    		torch.nn.Sigmoid(),
		torch.nn.Linear(H, H),
    		torch.nn.Sigmoid(),
    		torch.nn.Linear(H, D_out),
	)


# Use the optim package to define an Optimizer that will update the weights of
# the model for us. Here we will use Adam; the optim package contains many other
# optimization algoriths. The first argument to the Adam constructor tells the
# optimizer which Variables it should update.
loss_fn = torch.nn.MSELoss(size_average=False)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)


for epoch_index in range(epoch_num):
	for i, (batch, y) in enumerate(train_loader):
		batch = Variable(batch)
		y = Variable(y, requires_grad = False)

		# Forward pass: compute predicted y by passing x to the model.
    		y_pred = model(batch)

    		# Compute and print loss.
    		loss = loss_fn(y_pred, y.float())
    		print "[Epoch: "+str(epoch_index)+"/"+str(epoch_num)+"] [Batch: "+str(i)+"/"+str(len(dataset)/batch_size)+"] Loss:"+str(loss.data[0]/batch_size)

    		# Before the backward pass, use the optimizer object to zero all of the
    		# gradients for the variables it will update (which are the learnable weights
    		# of the model)
    		optimizer.zero_grad()

    		# Backward pass: compute gradient of the loss with respect to model
    		# parameters
    		loss.backward()

    		# Calling the step function on an Optimizer makes an update to its
    		# parameters
    		optimizer.step()


torch.save(model, "trained_model")
