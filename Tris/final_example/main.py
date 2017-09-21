#!/usr/bin/python

from kivy.config import Config
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '700')

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

import torch
from torch.autograd import Variable

import tris_ai as AI



class TrisMenuLayout(GridLayout):
	
	def setup(self):
		self.cols = 1
		self.rows = 2
		
		title_label = Label (text='[b]Tris[/b] [color=ff3333]AI[/color]', markup=True)
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
		inner_layout.add_widget(single_button)
		inner_layout.add_widget(Label())
		inner_layout.add_widget(Label())
		inner_layout.add_widget(multi_button)
		inner_layout.add_widget(Label())
		inner_layout.add_widget(Label())
		inner_layout.add_widget(exit_button)
		inner_layout.add_widget(Label())
		self.add_widget(inner_layout)
	


class TrisGameLayout(GridLayout):

	def __init__(self, trisgame):
		self.game = trisgame
		self.button_matrix = [[None for x in range(3)] for y in range(3)]

		self.turn_label = None

		self.player_name = [None, "Player 1", "Player 2"]		
		self.player_symbol = [None, "X", "O"]	
		self.player_color = [None, "ff3333", "1e90ff"]

		if self.game.player_number == 1:
			self.player_name[2] = "AI"	

		super(self.__class__, self).__init__()


	def button_pressed(self, x, y, btn):
		if self.game.player_number == 1 and self.game.turn == 2:
			print "Not your turn..."
			return
		
		else:
			self.execute_move(x, y)


	def execute_move(self, x = None, y = None):
		if x != None and y != None:	
			current_player = self.game.turn
			(move_performed, is_finished, winner) = self.game.perform_player_move(x, y)

		else:
			current_player = self.game.turn
			(move_performed, is_finished, winner) = self.game.perform_ai_move()

		if move_performed:
			self.turn_label.text = "[b]Turn:[/b] [color=" + self.player_color[self.game.turn] + "]" \
			+ self.player_name[self.game.turn] + "[/color]"	
				
			# Update Button Matrix
			for i in range(3):
				for j in range(3):
					if self.game.board_matrix[i][j] != "-":
						self.button_matrix[i][j].text = '[b][color=' + self.player_color[self.game.board_matrix[i][j]] +']' \
						+ self.player_symbol[self.game.board_matrix[i][j]] + '[/color][/b]'


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
		self.rows = 2
		
		self.turn_label = Label(text='[b]Turn:[/b] [color='+ self.player_color[self.game.turn] + ']' \
		+ self.player_name[self.game.turn] + '[/color]', markup=True)
		
		self.turn_label.font_size = 48
		
		inner_layout = GridLayout()
		inner_layout.rows = 3
		inner_layout.cols = 3
		inner_layout.padding = (8, 8)
		
		for x in range(3):
			for y in range(3):
				self.button_matrix[x][y] = Button(text="" + str(self.game.board_matrix[x][y]), font_size = 48, markup = True)
				if self.game.board_matrix[x][y] != "-":
					# Player 2 (AI) can have already placed his first move
					self.button_matrix[x][y].text = '[b][color=' + self.player_color[2] +']' + self.player_symbol[2] + '[/color][/b]'
				
				self.button_matrix[x][y].bind(on_press=partial (self.button_pressed, x, y))
				inner_layout.add_widget(self.button_matrix[x][y])
		self.add_widget(self.turn_label)
		inner_layout.size_hint=(2.5, 2)
		self.add_widget(inner_layout)
	

	def startup(self):	
		# If AI turn, AI move
		if self.game.player_number == 1 and self.game.turn == 2:
			self.execute_move()



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
			if self.board_matrix[x][0] == self.board_matrix[x][1] == self.board_matrix[x][2] \
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

		#(x, y) = AI.simple_move(self.board_matrix)
		#(x, y) = AI.random_move(self.board_matrix)
		#(x, y) = AI.minimax_move(self.board_matrix)
		#(x, y) = AI.minimaxalphabeta_move(self.board_matrix, self.turn)
		(x, y) = AI.nn_move(self.export_current_board(), model, self.turn)	
		#(x, y) = AI.cynical_random_move(self)

		print "AI move: (" + str(x) + ", " + str(y) + ")"
		print
		return self.perform_player_move(int(x), int(y))


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



class TrisApp(App):
	
	def build(self):
		menul = TrisMenuLayout()
		menul.setup()
		return menul



def start_game(player_number, obj):
	gamel = TrisGameLayout(TrisGame(player_number))
	gamel.setup()
	app.root.clear_widgets()
	app.root.add_widget(gamel)
	# Need to perform it in a new thread
	thread.start_new_thread(gamel.startup, ())



def open_menu(arg):
	menul = TrisMenuLayout()
	menul.setup()
	app.root.clear_widgets()
	app.root.add_widget(menul)



def close_app(arg):
	exit()

try:
	model = torch.load("trained_model")
except:
	print "No Model"

if __name__ == "__main__":
	app = TrisApp()
	app.run()
