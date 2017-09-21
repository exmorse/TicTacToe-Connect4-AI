#!/usr/bin/python

from kivy.config import Config
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock

from random import randint
from functools import partial
import time
import thread
import copy

import torch
from torch.autograd import Variable

import four_ai as AI



class ForzaMenuLayout(GridLayout):
	
	def setup(self):
		self.cols = 1
		self.rows = 2
		
		title_label = Label (text='[b]Forza[/b] [color=ff3333]4[/color]', markup=True)
		title_label.font_size = 42
		
		inner_layout = GridLayout()
		inner_layout.rows = 3
		inner_layout.cols = 3
		inner_layout.padding = (16, 16)
		
		single_button = Button(text = "[b]SinglePlayer[/b]", markup=True)
		single_button.font_size = 24
		single_button.bind(on_press=partial (start_game, 1))
	
		multi_button = Button(text = "[b]MultiPlayer[/b]", markup=True)
		multi_button.font_size = 24
		multi_button.bind(on_press=partial (start_game, 2))
			
		exit_button = Button(text = "[b]Exit[/b]", markup=True)
		exit_button.font_size = 24
		exit_button.bind(on_press=close_app)

		self.add_widget(title_label)
		inner_layout.add_widget(Label())
		inner_layout.add_widget(Label())
		inner_layout.add_widget(Label())
		inner_layout.add_widget(single_button)
		inner_layout.add_widget(multi_button)
		inner_layout.add_widget(exit_button)
		inner_layout.add_widget(Label())
		inner_layout.add_widget(Label())
		inner_layout.add_widget(Label())
		self.add_widget(inner_layout)
	


class ForzaGameLayout(GridLayout):

	def __init__(self, forzagame):
		self.game = forzagame
		self.label_matrix = [[None for col in range(7)] for row in range(6)]
		self.button_list = []

		self.turn_label = None

		self.player_name = [None, "Player 1", "Player 2"]		
		self.player_symbol = [None, "O", "O"]	
		self.player_color = [None, "ff3333", "1e90ff"]

		if self.game.player_number == 1:
			self.player_name[2] = "AI"	

		super(self.__class__, self).__init__()


	def button_pressed(self, col, btn):
		if self.game.player_number == 1 and self.game.turn == 2:
			print "Not your turn..."
			return
		
		else:
			self.execute_move(col)


	def execute_move(self, col = None):
		if col != None:	
			current_player = self.game.turn
			(move_performed, is_finished, winner) = self.game.perform_player_move(col)

		else:
			current_player = self.game.turn
			(move_performed, is_finished, winner) = self.game.perform_ai_move()

		if move_performed:
			self.turn_label.text = "[b]Turn:[/b] [color=" + self.player_color[self.game.turn] + "]" \
			+ self.player_name[self.game.turn] + "[/color]"	
				
			# Update Button Matrix
			for col in range(7):
				for row in range(6):
					if self.game.board_matrix[row][col] != "-":
						self.label_matrix[row][col].text = '[b][color=' + self.player_color[self.game.board_matrix[row][col]] +']' \
						+ self.player_symbol[self.game.board_matrix[row][col]] + '[/color][/b]'


			if is_finished:
				if winner == 0:
					popup_content=Label(text="It's a draw!")
				else: 
					popup_content=Label(text=self.player_name[winner] + " won!")
				
				popup = Popup(title='Game Over',
				content=popup_content,
				size_hint=(None, None), size=(200, 200))
				popup.bind(on_dismiss=open_menu)
				popup.open()

			else:
				# If AI turn then AI move
				if self.game.player_number == 1 and self.game.turn == 2:
					thread.start_new_thread(self.execute_move, ())
			

	def setup(self):
		self.cols = 1
		self.rows = 3
		
		self.turn_label = Label(text='[b]Turn:[/b] [color='+ self.player_color[self.game.turn] + ']' \
		+ self.player_name[self.game.turn] + '[/color]', markup=True)
		
		self.turn_label.font_size = 48
		
		inner_layout = GridLayout()
		inner_layout.rows = 6
		inner_layout.cols = 7
		inner_layout.padding = (8, 8)
		
		for row in range(6):
			for col in range(7):
				self.label_matrix[row][col] = Label(text=str(self.game.board_matrix[row][col]), font_size = 48, markup = True)
				if self.game.board_matrix[row][col] != "-":
					# Player 2 (AI) can have already placed his first move
					self.label_matrix[row][col].text = '[b][color=' + self.player_color[2] +']' + self.player_symbol[2] + '[/color][/b]'
				
				#self.button_matrix[x][y].bind(on_press=partial (self.button_pressed, x, y))
				inner_layout.add_widget(self.label_matrix[row][col])
		
		self.add_widget(self.turn_label)
		inner_layout.size_hint=(2.5, 2)
		self.add_widget(inner_layout)

		# Row of Button, one for each column
		button_row_layout = GridLayout()
		button_row_layout.rows = 1
		button_row_layout.cols = 7 
		for col in range(7):
			button = Button(text="[b]O[/b]", font_size = 40, markup = True)
			button.bind(on_press=partial(self.button_pressed, col))	
			button_row_layout.add_widget(button)	

		button_row_layout.size_hint=(0.5, 0.5)
		self.add_widget(button_row_layout)

	def startup(self):	
		# If AI turn, AI move
		if self.game.player_number == 1 and self.game.turn == 2:
			self.execute_move()



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

		#col = AI.simple_move(self)
		#col = AI.random_move(self)
		#col = AI.minimax_move(self)
		#col = AI.minimaxalphabeta_move(self)
		col = AI.nn_move(self, model, self.turn)
		#col = AI.cynical_random_move(self)
		#col = AI.cynical_defensive_random_move(self)
		#col = AI.nn_minimax_move(self, model, self.turn)

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

class ForzaApp(App):
	
	def build(self):
		menul = ForzaMenuLayout()
		menul.setup()
		return menul



def start_game(player_number, obj):
	gamel = ForzaGameLayout(ForzaGame(player_number))
	gamel.setup()
	app.root.clear_widgets()
	app.root.add_widget(gamel)
	# Need to perform it in a new thread
	thread.start_new_thread(gamel.startup, ())



def open_menu(arg):
	menul = ForzaMenuLayout()
	menul.setup()
	app.root.clear_widgets()
	app.root.add_widget(menul)



def close_app(arg):
	exit()




if __name__ == "__main__":
	try:
        	model = torch.load("trained_model_1995")
	except:
        	print "No Model"
	app = ForzaApp()
	app.run()
