#!/usr/bin/python

from random import randint
from functools import partial
import time
import thread
import pprint
import json
import copy

import torch
from torch.autograd import Variable

import tris_ai as AI


class TrisGame:

	def __init__(self, player_number):
		# If player_number == 1 then AI plays against Player 1
		self.player_number = player_number
		self.board_matrix = [['-' for x in range(3)] for y in range(3)]
		self.turn = randint(1, 2)
		self.finished = False
		self.winner = None
		self.piece_number = [None, 0, 0]


	def check_winner(self):
		if self.piece_number[1] < 3 and self.piece_number[2] < 3:
			return (False, None)

		# Check Cols
		for x in range(3):
			if self.board_matrix[x][0]== self.board_matrix[x][1] == self.board_matrix[x][2] \
			and self.board_matrix[x][0] != "-":
				print "Victory Condition 1" + ": "  + "Player " + str(self.board_matrix[x][0])
				return (True, self.board_matrix[x][0])	

		# Check Rows
		for y in range(3):
			if self.board_matrix[0][y] == self.board_matrix[1][y] == self.board_matrix[2][y] \
			and self.board_matrix[0][y] != "-":
				print "Victory Condition 2" + ": "  + "Player " + str(self.board_matrix[0][y])
				return (True, self.board_matrix[0][y])	

		# Check Diagonals
		if self.board_matrix[0][0] == self.board_matrix[1][1] == self.board_matrix[2][2] \
		and self.board_matrix[1][1] != "-":
			print "Victory Condition 3" + ": "  + "Player " + str(self.board_matrix[1][1])
			return (True, self.board_matrix[1][1])	
		if self.board_matrix[0][2] == self.board_matrix[1][1] == self.board_matrix[2][0] \
		and self.board_matrix[1][1] != "-":
			print "Victory Condition 4" + ": "  + "Player " + str(self.board_matrix[1][1])
			return (True, self.board_matrix[1][1])	
				
		# Check Draw
		if self.piece_number[1] + self.piece_number[2] == 9:
			print "Draw"
			return (True, 0)	

		return (False, None) 


	def perform_player_move(self, x, y):
		if self.board_matrix[x][y] == "-":
			self.board_matrix[x][y] = self.turn
			self.piece_number[self.turn] += 1
			
			(is_finished, winner) = self.check_winner()
			if is_finished:
				self.finished = True
				self.winner = winner
				self.turn = 3 - self.turn
				return (True, is_finished, winner)

			else:
				self.turn = 3 - self.turn
				return (True, False, None)	
					
		else:
			print "Move not allowed"
			return (False, False, None)


	def perform_ai_move(self, p1_style, p2_style):
		#print "AI move: thinking..."

		# ***************************
		# *** Select AI algorithm ***
		# ***************************

		if self.turn == 1:
			if p1_style == 0:
				#(x, y) = AI.random_move(self.board_matrix)
				(x, y) = AI.cynical_random_move(self)
			#elif p1_style == 1:
			#	(x, y) = AI.nn_move(self.export_current_board(), model, self.turn)
			else:
				(x, y) = AI.minimaxalphabeta_move(self.board_matrix, self.turn)

		else:
			if p2_style == 0:
				#(x, y) = AI.random_move(self.board_matrix)
				(x, y) = AI.cynical_random_move(self)
			#else:
			#	(x, y) = AI.nn_move(self.export_current_board(), model, self.turn)
			else: 
				(x, y) = AI.minimaxalphabeta_move(self.board_matrix, self.turn)
			
			#if opponent == 0:
			#	(x, y) = AI.minimaxalphabeta_move(self.board_matrix, self.turn)
			#else:
			##	(x, y) = AI.random_move(self.board_matrix)

			#(x, y) = AI.simple_move(self.board_matrix)
			#if randint(0,8) != 0:
			#	(x, y) = AI.random_move(self.board_matrix)
		#(x, y) = AI.minimax_move(self.board_matrix)
			#else:
			#	(x, y) = AI.minimaxalphabeta_move(self.board_matrix, self.turn)
		#(x, y) = AI.nn_move(self.export_current_board(), model, self.turn)

		#print "AI move: (" + str(x) + ", " + str(y) + ")"
		#print
		
		return self.perform_player_move(int(x), int(y))

	def print_board(self):
		print self.board_matrix

	# Export current board as a list for neural network dataset
	# '-' -> 0 
	def export_current_board(self):
		export_board = []
		for i in range(3):
			export_board.extend(self.board_matrix[i])

		board_1 = [1 if x==1 else 0 for x in export_board]
		board_2 = [1 if x==2 else 0 for x in export_board]
		board_3 = [1 if x=='-' else 0 for x in export_board]
		return board_1 + board_2 + board_3



def rotate(array_b):
        new_b = [-1 for r in range(27)]
    
        for i in range(3):
                new_b[i*9+0] = array_b[i*9+6] 
                new_b[i*9+1] = array_b[i*9+3] 
                new_b[i*9+2] = array_b[i*9+0] 
                new_b[i*9+3] = array_b[i*9+7] 
                new_b[i*9+4] = array_b[i*9+4] 
                new_b[i*9+5] = array_b[i*9+1] 
                new_b[i*9+6] = array_b[i*9+8] 
                new_b[i*9+7] = array_b[i*9+5] 
                new_b[i*9+8] = array_b[i*9+2] 
    
        return new_b




try:
	model = torch.load("trained_model")
except:
	print "No model..."	

if __name__ == "__main__":
	
	dataset_struct = []
	
	game_num = 50000
	win = 0
	draw = 0

	position_dict = {}

	for iteration in range(game_num):
		game = TrisGame(0)
		move_history = []

		p1_style = randint(0,1)
		p2_style = 1-p1_style	

		while not game.finished:
			game.perform_ai_move(0, 0)
			if game.turn == 2:
				move_history.append(game.export_current_board())

		if game.winner == 1:
			result = 100
			win = win + 1
		elif game.winner == 2:
			result = -100
		else:
			draw = draw + 1
			result = 50

		for ind, el in enumerate(move_history):
			
			d_el = {}
			d_el["state"] = el
			
			## ----------------------------
			## --------- SCALATO ----------
			## ----------------------------
			d_el["result"] = result * (ind + 1) / len(move_history)
			
			dataset_struct.append(d_el)

			n_el = copy.deepcopy(el)
                       	for r in range(3):
				n_el = rotate(n_el)
				d_el = {}
                               	d_el["state"] = copy.deepcopy(n_el)
				d_el["result"] = result * (ind + 1) / len(move_history)
                                dataset_struct.append(d_el)

		print "Iteration " + str(iteration)  + " of " + str(game_num)

	print "\n\n" + str(win) + " / " + str(game_num) + " (" + str(draw) + ")"

	with open("rotate_cynical_dataset.json", "w+") as outFile:
		outFile.write(json.dumps(dataset_struct))

