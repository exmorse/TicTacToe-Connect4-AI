#!/usr/bin/python
# -*- coding: utf-8 -*-

import torch
from torch.autograd import Variable
from random import randint
import json
import pprint

with open("single_dataset.json") as dataset_file:
	dataset = json.load(dataset_file)

# N is batch size; D_in is input dimension;
# H is hidden dimension; D_out is output dimension.
N, D_in, H, D_out = len(dataset), 126, 180, 1

# Create random Tensors to hold inputs and outputs, and wrap them in Variables.
x = Variable(torch.randn(N, D_in))
y = Variable(torch.randn(N, D_out), requires_grad=False)

for i in range(N):
	for j in range(D_in):
		x.data[i, j] = dataset[i]["state"][j]

	y.data[i, 0] = dataset[i]["result"]


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


loss_fn = torch.nn.MSELoss(size_average=False)

# Use the optim package to define an Optimizer that will update the weights of
# the model for us. Here we will use Adam; the optim package contains many other
# optimization algoriths. The first argument to the Adam constructor tells the
# optimizer which Variables it should update.
learning_rate = 0.005
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
for t in range(500):
    # Forward pass: compute predicted y by passing x to the model.
    y_pred = model(x)

    # Compute and print loss.
    loss = loss_fn(y_pred, y)
    print(t, loss.data[0]/N)

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
