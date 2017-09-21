from random import randint
import copy
from torch.autograd import Variable
import torch

def simple_move(board_matrix):
	#print "AI: " + str(board_matrix)
	for x in range(3):
		for y in range(3):
			if board_matrix[x][y] == "-":
				return (x, y)

	return (None, None)


def nn_move(nn_matrix, model, player):
	maxi = -2000
	best = -1

	if player == 2:
		for i in range(9):
			nn_matrix[i], nn_matrix[9+i] = nn_matrix[9+i], nn_matrix[i]
		#nn_matrix = [-x if x != 0 else 0 for x in nn_matrix]

	for ind in range(9):
		if nn_matrix[ind] == 0 and nn_matrix[9+ind] == 0 and nn_matrix[18+ind] == 1:
			nn_matrix[ind] = 1
			nn_matrix[18+ind] = 0
			estimation = model(Variable(torch.Tensor([nn_matrix]))).data[0, 0]
			print estimation			
			
			if estimation > maxi:
				maxi = estimation
				best = ind
		
			nn_matrix[ind] = 0
			nn_matrix[18+ind] = 1

	print "Best move: " + str(best)
	x = best / 3
	y = best % 3
	
	return (x, y)
	

def random_move(board_matrix):
	done_move = False
	while not done_move:
		x = randint(0, 2)
		y = randint(0, 2)

		if board_matrix[x][y] == "-":
			return (x, y)


def cynical_random_move(game):
	for i in range(3):
		for j in range(3):
			if game.board_matrix[i][j] == '-':
				game.board_matrix[i][j] = game.turn
				game.piece_number[game.turn] = game.piece_number[game.turn] + 1
				(finished, winner) = game.check_winner()
				game.board_matrix[i][j] = '-'
				game.piece_number[game.turn] = game.piece_number[game.turn] - 1
				if finished:
					return (i, j)

	return random_move(game.board_matrix)

def defensive_cynical_random_move(board_matrix):
	return cynical_random_move(board_matrix)


def minimax_move(board_matrix):
	tree = MiniMaxTree(board_matrix)
	return tree.getBestMove()

class MiniMaxTree():
	player_symbol = [None, "X", "O"]
	purpose_array = ["Max", "Min"]		

	def __init__(self, initial_board, purpose = 0, player = 2, parent_move = None):
		self.board_matrix = copy.deepcopy(initial_board)
		self.final_situation = False
		self.winner = None
		self.child_nodes = []
		self.value = 0
		self.player = player
		self.parent_move = parent_move
		self.purpose = purpose
		
		(self.final_situation, self.winner) = self.isFinalSituation()
		
		if self.final_situation:
			if self.winner == 1:
				self.value = -1
			elif self.winner == 2:
				self.value = 1
			else:
				self.value = 0
		else:
			self.generateSubtree()
			
			if self.purpose_array[self.purpose] == "Max":
				self.value = -1 
				for child in self.child_nodes:
					if child.value > self.value:
						self.value = child.value

			if self.purpose_array[self.purpose] == "Min":
				self.value = 1 
				for child in self.child_nodes:
					if child.value < self.value:
						self.value = child.value


	def isFinalSituation(self):
		# Check Cols
		for x in range(3):
                	if self.board_matrix[x][0]== self.board_matrix[x][1] == self.board_matrix[x][2] \
			and self.board_matrix[x][0] != "-":
                                return (True, self.board_matrix[x][0])  

                # Check Rows
                for y in range(3):
                        if self.board_matrix[0][y] == self.board_matrix[1][y] == self.board_matrix[2][y] \
                        and self.board_matrix[0][y] != "-":
                                return (True, self.board_matrix[0][y])  

                # Check Diagonals
                        if self.board_matrix[0][0] == self.board_matrix[1][1] == self.board_matrix[2][2] \
                        and self.board_matrix[1][1] != "-":
                                return (True, self.board_matrix[1][1])  
                        if self.board_matrix[0][2] == self.board_matrix[1][1] == self.board_matrix[2][0] \
                        and self.board_matrix[1][1] != "-":
                                return (True, self.board_matrix[1][1])

		# Check Not Draw
		for x in range(3):
			for y in range(3):
				if self.board_matrix[x][y] == "-":
					return (False, None)

		# Draw
                return (True, 0) 

	def generateSubtree(self):
		for x in range(3):
			for y in range(3):
				if self.board_matrix[x][y] == "-":
					new_board = copy.deepcopy(self.board_matrix)
					new_board[x][y] = self.player
					self.child_nodes.append(MiniMaxTree(new_board, purpose = 1-self.purpose, \
					player=(3-self.player), parent_move = (x, y)))
		
	def getBestMove(self):
		for child in self.child_nodes:
			if child.value == self.value:
				return child.parent_move



def minimaxalphabeta_move(board_matrix, player_turn):
	tree = MiniMaxAlphaBetaPruningTree(board_matrix, initial_player = player_turn, player = player_turn)
	return tree.getBestMove()

class MiniMaxAlphaBetaPruningTree(MiniMaxTree):
	def __init__(self, initial_board, initial_player, player, purpose = 0, parent_move = None, alpha = -2, beta = 2):

		self.board_matrix = copy.deepcopy(initial_board)
		self.final_situation = False
		self.winner = None
		self.child_nodes = []
		self.value = 0
		self.initial_player = copy.deepcopy(initial_player)
		self.player = copy.deepcopy(player)
		self.parent_move = parent_move
		self.purpose = purpose
		
		# Alpha : Minimum value for MAX found on current path
		# Beta  : Maximum value for MIN found on current path
		self.alpha = alpha
		self.beta = beta

		(self.final_situation, self.winner) = self.isFinalSituation()

		if self.final_situation:
			if self.winner == self.initial_player:
				self.value = 1
			elif self.winner == 3 - self.initial_player:
				self.value = -1
			else:
				self.value = 0
		else:
			self.generateSubtree()
			
			if self.purpose_array[self.purpose] == "Max":
				self.value = -1 
				for child in self.child_nodes:
					if child.value > self.value:
						self.value = child.value

			if self.purpose_array[self.purpose] == "Min":
				self.value = 1 
				for child in self.child_nodes:
					if child.value < self.value:
						self.value = child.value

	
	def generateSubtree(self):
		for x in range(3):
			for y in range(3):
				if self.board_matrix[x][y] == "-":
					new_board = copy.deepcopy(self.board_matrix)
					new_board[x][y] = self.player
					child = MiniMaxAlphaBetaPruningTree(new_board, purpose = 1-self.purpose, \
						initial_player = self.initial_player, player = (3-self.player), parent_move = (x, y), \
						alpha = self.alpha, beta = self.beta)

					self.child_nodes.append(child)	
					
					if self.purpose_array[self.purpose] == "Max":
						if child.value > self.alpha:
							self.alpha = child.value
					
						if self.beta <= self.alpha:
							#Pruning
							return
					
					if self.purpose_array[self.purpose] == "Min":
						if child.value < self.beta:
							self.beta = child.value
					
						if self.beta <= self.alpha:
							#Pruning
							return

