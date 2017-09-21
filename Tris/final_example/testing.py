#!/usr/bin/python

from random import randint
from functools import partial
import time
import thread
import pprint
import json

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


	def perform_ai_move(self):
		#print "AI move: thinking..."

		# ***************************
		# *** Select AI algorithm ***
		# ***************************

		if self.turn == 1:
			(x, y) = AI.nn_move(self.export_current_board(), model, self.turn)
			#(x, y) = AI.random_move(self.board_matrix)
			#(x, y) = AI.minimaxalphabeta_move(self.board_matrix, self.turn)

		else:
			(x, y) = AI.random_move(self.board_matrix)
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


try:
	model = torch.load("trained_model")
except:
	print "No model..."	

if __name__ == "__main__":
	
	dataset_struct = []
	
	game_num = 2000
	win = 0
	draw = 0

	position_dict = {}

	for iteration in range(game_num):
		game = TrisGame(0)
		move_history = []
		player_history = []

		while not game.finished:
			game.perform_ai_move()
			move_history.append(game.export_current_board())
			player_history.append(game.turn)			

		if game.winner == 1:
			result = 100
			win = win + 1
		elif game.winner == 2:
			result = -100
		else:
			draw = draw + 1
			result = 0

		print "Iteration " + str(iteration)  + " of " + str(game_num)

	print "\n\n" + str(win) + " / " + str(game_num) + " (" + str(draw) + ")"

