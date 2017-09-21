#!/usr/bin/python

from random import randint
from functools import partial
import time
import thread
import copy
import json

import torch
from torch.autograd import Variable

import four_ai as AI


class ForzaGame:

	def __init__(self, player_number):
		# If player_number == 1 then AI plays against Player 1
		self.player_number = player_number
		self.board_matrix = [['-' for col in range(7)] for row in range(6)]
		self.turn = randint(1, 2)
		self.finished = False
		self.winner = None
		self.piece_number = [None, 0, 0]
		self.first_free_row = [5 for col in range(7)]
		self.count_player_cols = [0]
		self.count_player_rows = [0]

		for p in range(1, 3):
			d_col = {}
			for col in range(7):
				d_col[col] = 0
			
			d_row = {}
			for row in range(7):
				d_row[row] = 0
			
			self.count_player_cols.append(d_col)
			self.count_player_rows.append(d_row)
				

	def check_winner(self):
		if self.piece_number[1] < 4 and self.piece_number[2] < 4:
			return (False, None)

		for p in [1,2]:
			for c in range(7):
				if self.count_player_cols[p][c] >= 4:	
					# Check Column c
					if self.check_player_for_col(p, c):
						return (True, p) 
					
					pass

		for p in [1,2]:
			for r in range(6):
				if self.count_player_rows[p][r] >= 4:	
					# Check Row r
					if self.check_player_for_row(p, r):
						return (True, p) 
					
					pass

		# Check Diagonal			
		for c in range(7):
			if c + 3 < 7:
				for r in range(6):
					if r + 3 < 6:
						count = 0
						mc = copy.copy(c)
						mr = copy.copy(r)
						for i in range(4):
							if self.board_matrix[mr+i][mc+i] == self.turn:
								count += 1
							else:
								pass

						if count == 4:
							return (True, self.turn)
		for c in range(7):
			if c - 3 >= 0:
				for r in range(6):
					if r + 3 < 6:
						count = 0
						mc = copy.copy(c)
						mr = copy.copy(r)
						for i in range(4):
							if self.board_matrix[mr+i][mc-i] == self.turn:
								count += 1
							else:
								pass

						if count == 4:
							return (True, self.turn)
				
	
		# Check Draw
		if self.piece_number[1] + self.piece_number[2] == 42:
			return (True, 0)	

		return (False, None) 

	def check_player_for_col(self, p, c, length=4):
		count = 0
		for r in range(0, 6):
			if self.board_matrix[r][c] == p:
				count += 1
			else: 
				count = 0
			if count == length:
				return True
	
		return False

	def check_player_for_row(self, p, r, length=4):
		count = 0
		for c in range(0, 7):
			if self.board_matrix[r][c] == p:
				count += 1
			else: 
				count = 0
			if count == length:
				return True
	
		return False

	def perform_player_move(self, col):
		if self.board_matrix[self.first_free_row[col]][col] == "-":
			self.board_matrix[self.first_free_row[col]][col] = self.turn
	
			self.count_player_cols[self.turn][col] += 1
			self.count_player_rows[self.turn][self.first_free_row[col]] += 1

			self.first_free_row[col]-=1
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
		print "AI move: thinking..."

		# ***************************
		# *** Select AI algorithm ***
		# ***************************

		if self.turn == 1:
			col = AI.nn_move(self, model, self.turn)
		
		if self.turn == 2:
			#col = AI.cynical_random_move(self)
			col = AI.cynical_defensive_random_move(self)
			#col = AI.random_move(self)
		
		#col = AI.simple_move(self)
		#col = AI.random_move(self)
		#col = AI.minimaxalphabeta_move(self)

		print "AI inserts in column " + str(col)
		print
		return self.perform_player_move(int(col))


	def export_current_board(self):
                export_board = []
                for i in range(6):
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
                game = ForzaGame(0)

                while not game.finished:
                        game.perform_ai_move()

                if game.winner == 1:
                        result = 100
                        win = win + 1
                elif game.winner == 2:
                        result = -100
                else:
                        draw = draw + 1
                        result = 50

                print "Iteration " + str(iteration)  + " of " + str(game_num)

        print "\n\n" + str(win) + " / " + str(game_num) + " (" + str(draw) + ")"
