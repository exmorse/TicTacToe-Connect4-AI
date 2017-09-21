from random import randint
import copy
import torch
from torch.autograd import Variable


def simple_move(game):
	for col in range(7):
		if game.board_matrix[game.first_free_row[col]][col] == "-":
			return col
	return (None, None)


def random_move(game):
	done_move = False
	while not done_move:
		col = randint(0, 6)
		if game.board_matrix[game.first_free_row[col]][col] == "-":
			return col


def nn_move(game, model, player):
        maxi = -2000
        best = -1

	original_matrix = copy.deepcopy(game.board_matrix)
	
        if game.turn == 2:
		for i in range(6):
			for j in range(7):
				game.board_matrix[i][j] = 3 - game.board_matrix[i][j] if game.board_matrix[i][j] != '-' else '-'		

        for col in range(7):
        	if game.board_matrix[game.first_free_row[col]][col] == '-':
			
			# Update
			game.board_matrix[game.first_free_row[col]][col] = 1
			 
			nn_matrix = game.export_current_board()
			estimation = model(Variable(torch.Tensor([nn_matrix]))).data[0, 0]
                        print estimation    
    
                        if estimation > maxi:
                                maxi = estimation
                                best = col 
    
			# Reset
			game.board_matrix[game.first_free_row[col]][col] = '-'

	game.board_matrix = copy.deepcopy(original_matrix)
        
	print "Best move: " + str(best)
    
        return best


def cynical_random_move(game):
        for col in range(7):
        	if game.board_matrix[game.first_free_row[col]][col] == '-':
			# Update
			game.board_matrix[game.first_free_row[col]][col] = game.turn
                        game.count_player_cols[game.turn][col] += 1
                        game.count_player_rows[game.turn][game.first_free_row[col]] += 1
                        game.first_free_row[col] -= 1
                        game.piece_number[game.turn] += 1
						 
			(finished, winner) = game.check_winner()
                        
			# Reset
                        game.first_free_row[col] += 1
                        game.piece_number[game.turn] -= 1
			game.board_matrix[game.first_free_row[col]][col] = '-'
                        game.count_player_cols[game.turn][col] -= 1
                        game.count_player_rows[game.turn][game.first_free_row[col]] -= 1

			if finished:
                        	return col
				
        return random_move(game)

def cynical_defensive_random_move(game):
        for col in range(7):
        	if game.board_matrix[game.first_free_row[col]][col] == '-':
			
			# Update
			game.board_matrix[game.first_free_row[col]][col] = game.turn
                        game.count_player_cols[game.turn][col] += 1
                        game.count_player_rows[game.turn][game.first_free_row[col]] += 1
                        game.first_free_row[col] -= 1
                        game.piece_number[game.turn] += 1
		
			# Check if i can win				 
			(finished, winner) = game.check_winner()
                        
			# Reset
                        game.first_free_row[col] += 1
                        game.piece_number[game.turn] -= 1
			game.board_matrix[game.first_free_row[col]][col] = '-'
                        game.count_player_cols[game.turn][col] -= 1
                        game.count_player_rows[game.turn][game.first_free_row[col]] -= 1

			if finished:
                        	return col

			# Update with opponent move
			other_turn = 3 - game.turn
			game.board_matrix[game.first_free_row[col]][col] = other_turn
                        game.count_player_cols[other_turn][col] += 1
                        game.count_player_rows[other_turn][game.first_free_row[col]] += 1
                        game.first_free_row[col] -= 1
                        game.piece_number[other_turn] += 1

			# Check if he can win
			(opponent_finished, winner) = game.check_winner()

			# Reset
                        game.first_free_row[col] += 1
                        game.piece_number[other_turn] -= 1
			game.board_matrix[game.first_free_row[col]][col] = '-'
                        game.count_player_cols[other_turn][col] -= 1
                        game.count_player_rows[other_turn][game.first_free_row[col]] -= 1

			if opponent_finished:
				return col

	# Else return random
	return random_move(game)
				

def minimax_move(game):
	tree = MiniMaxTree(game)
	return tree.getBestMove()

class MiniMaxTree():
	player_symbol = [None, "X", "O"]
	purpose_array = ["Max", "Min"]		

	def __init__(self, initial_game, purpose = 0, player = 2, parent_move = None):
		self.game = copy.deepcopy(initial_game)
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
		if self.game.piece_number[1] < 4 and self.game.piece_number[2] < 4:
                        return (False, None)

                for p in [1,2]:
                        for c in range(7):
                                if self.game.count_player_cols[self.player][c] >= 4:   
                                        # Check Column c
                                        if self.game.check_player_for_col(self.player, c): 
                                                #print "(Col) Potential Ending for player " + str(self.player)
						return (True, self.player)  
                                                    
                                        pass

                for p in [1,2]:
                        for r in range(6):
                                if self.game.count_player_rows[self.player][r] >= 4:   
                                        # Check Row r
                                        if self.game.check_player_for_row(self.player, r): 
                                                #print "(Row) Potential Ending for player " + str(self.player)
                                                return (True, self.player)  
    
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
                                                        if self.game.board_matrix[mr+i][mc+i] == self.player:
                                                                count += 1
                                                        else:
                                                                pass

                                                if count == 4:
                                                	#print "(Diag) Potential Ending for player " + str(self.player)
                                                        return (True, self.player)
                for c in range(7):
                        if c - 3 >= 0:
                                for r in range(6):
                                        if r + 3 < 6:
                                                count = 0
                                                mc = copy.copy(c)
                                                mr = copy.copy(r)
                                                for i in range(4):
                                                        if self.game.board_matrix[mr+i][mc-i] == self.player:
                                                                count += 1
                                                        else:
                                                                pass
                                                if count == 4:
                                                	#print "(Diag) Potential Ending for player " + str(self.player)
                                                        return (True, self.player)

		# Check Draw
                if self.game.piece_number[1] + self.game.piece_number[2] == 42:
                        return (True, 0)

                return (False, None)


	def generateSubtree(self):
		for col in range(7):
			if self.game.board_matrix[self.game.first_free_row[col]][col] == "-":
				new_game = copy.deepcopy(self.game)
				new_game.board_matrix[new_game.first_free_row[col]][col] = self.player
				
				new_game.count_player_cols[self.player][col] += 1
                        	new_game.count_player_rows[self.player][new_game.first_free_row[col]] += 1

                        	new_game.first_free_row[col]-=1
                        	new_game.piece_number[self.player] += 1

				self.child_nodes.append(MiniMaxTree(new_game, purpose = 1-self.purpose, \
				player=(3-self.player), parent_move = col))
		
	def getBestMove(self):
		for child in self.child_nodes:
			if child.value == self.value:
				return child.parent_move



def minimaxalphabeta_move(game):
	#if game.piece_number[2] <= 13:
	#	print "Random move..."
	#	return random_move(game)

	#print "MinMax move..."
	tree = MiniMaxAlphaBetaPruningTree(game)
	return tree.getBestMove()

class MiniMaxAlphaBetaPruningTree(MiniMaxTree):
	
	max_depth = 5

	def __init__(self, initial_game, purpose = 0, player = 2, parent_move = None, alpha = -2, beta = 2, depth = 0):
		self.game = copy.deepcopy(initial_game)
		self.final_situation = False
		self.winner = None
		self.child_nodes = []
		self.value = 0
		self.player = player
		self.parent_move = parent_move
		self.purpose = purpose
		self.depth = depth		

		# Alpha : Minimum value for MAX found on current path
		# Beta  : Maximum value for MIN found on current path
		self.alpha = alpha
		self.beta = beta

		(self.final_situation, self.winner) = self.isFinalSituation()
	
		# Final configuration	
		if self.final_situation:
			if self.winner == 1:
				self.value = -1
			elif self.winner == 2:
				self.value = 1
			else:
				self.value = 0
		
		# Not final configuration
		else:
			# Generate subtree, and get value from children
			if self.depth < self.max_depth:
				self.generateSubtree()
			
				if self.purpose_array[self.purpose] == "Max" and len(self.child_nodes) > 0:
					self.value = -1 
					for child in self.child_nodes:
						if child.value > self.value:
							self.value = child.value

				elif self.purpose_array[self.purpose] == "Min" and len(self.child_nodes) > 0:
					self.value = 1 
					for child in self.child_nodes:
						if child.value < self.value:
							self.value = child.value

			# No children and not final configuration
			# Use heuristics to estimate value
			else:
				self.value = self.heuristicValue()

				
		# Debug
		if self.depth == 0:
			vls = []
			for c in self.child_nodes:
				vls.append(c.value)

			print vls
			print "Best: " + str(self.value)


	def heuristicValue(self):
		#return randint(0,9)*0.1
		r = self.game.first_free_row[self.parent_move] + 1
		c = self.parent_move
		b = self.game.board_matrix
		
		score = 0

		# Middle area concentration
		p = self.player
		o = 3-self.player
		for mr in [2, 3, 4, 5]:
			for mc in [2, 3, 4]:
				if b[mr][mc] == p:
					score = score + 0.01
				if b[mr][mc] == o:
					score = score - 0.01 

		score = score + self.numberOfOpenTwo() * 0.01
		score = score + self.numberOfOpenThree() * 0.06 

		if self.player == 1:
			return -score

		return score
	

	def numberOfOpenTwo(self):
		ot = 0

                for p in [1,2]:
                        for c in range(7):
                                if self.game.count_player_cols[self.player][c] >= 3:   
                                        # Check Column c
                                        if self.game.check_player_for_col(self.player, c, length=2): 
                                        	ot += 1 

                for p in [1,2]:
                        for r in range(6):
                                if self.game.count_player_rows[self.player][r] >= 3:   
                                        # Check Row r
                                        if self.game.check_player_for_row(self.player, r, length=2): 
                                         	ot += 1 
    
		# Check Diagonal                        
                for c in range(7):
                        if c + 1 < 7:
                                for r in range(6):
                                        if r + 1 < 6:
                                                count = 0 
                                                mc = copy.copy(c)
                                                mr = copy.copy(r)
                                                for i in range(2):
                                                        if self.game.board_matrix[mr+i][mc+i] == self.player:
                                                                count += 1
                                                        else:
                                                                pass

                                                if count == 2:
                					ot += 1
		for c in range(7):
                        if c - 1 >= 0:
                                for r in range(6):
                                        if r + 1 < 6:
                                                count = 0
                                                mc = copy.copy(c)
                                                mr = copy.copy(r)
                                                for i in range(2):
                                                        if self.game.board_matrix[mr+i][mc-i] == self.player:
                                                                count += 1
                                                        else:
                                                                pass
                                                if count == 2:
							ot += 1


		return ot
	

	def numberOfOpenThree(self):
		ot = 0

                for p in [1,2]:
                        for c in range(7):
                                if self.game.count_player_cols[self.player][c] >= 3:   
                                        # Check Column c
                                        if self.game.check_player_for_col(self.player, c, length=3): 
                                        	ot += 1 

                for p in [1,2]:
                        for r in range(6):
                                if self.game.count_player_rows[self.player][r] >= 3:   
                                        # Check Row r
                                        if self.game.check_player_for_row(self.player, r, length=3): 
                                         	ot += 1 
    
		# Check Diagonal                        
                for c in range(7):
                        if c + 2 < 7:
                                for r in range(6):
                                        if r + 2 < 6:
                                                count = 0 
                                                mc = copy.copy(c)
                                                mr = copy.copy(r)
                                                for i in range(3):
                                                        if self.game.board_matrix[mr+i][mc+i] == self.player:
                                                                count += 1
                                                        else:
                                                                pass

                                                if count == 3:
                					ot += 1
		for c in range(7):
                        if c - 2 >= 0:
                                for r in range(6):
                                        if r + 2 < 6:
                                                count = 0
                                                mc = copy.copy(c)
                                                mr = copy.copy(r)
                                                for i in range(3):
                                                        if self.game.board_matrix[mr+i][mc-i] == self.player:
                                                                count += 1
                                                        else:
                                                                pass
                                                if count == 3:
							ot += 1


		return ot
	

	def generateSubtree(self):
		for col in range(7):
			if self.game.board_matrix[self.game.first_free_row[col]][col] == "-":
				new_game = copy.deepcopy(self.game)
				new_game.board_matrix[new_game.first_free_row[col]][col] = self.player
				
				new_game.count_player_cols[self.player][col] += 1
                        	new_game.count_player_rows[self.player][new_game.first_free_row[col]] += 1

                        	new_game.first_free_row[col]-=1
                        	new_game.piece_number[self.player] += 1

				child = MiniMaxAlphaBetaPruningTree (new_game, purpose = 1-self.purpose, \
				player=(3-self.player), parent_move = col, depth = self.depth + 1)
		

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


def nn_minimax_move(game, model, player):
	tree = MiniMaxNeuralNetworkTree(game, model, initial_player = player, player = player)
	return tree.getBestMove()

class MiniMaxNeuralNetworkTree(MiniMaxTree):
	
	max_depth = 5

	def __init__(self, initial_game, model, initial_player, player, purpose = 0, parent_move = None, alpha = -200, beta = 200, depth = 0):
		self.game = copy.deepcopy(initial_game)
		self.final_situation = False
		self.winner = None
		self.child_nodes = []
		self.value = 0
		self.initial_player = copy.deepcopy(initial_player)
		self.player = copy.deepcopy(player)
		self.parent_move = parent_move
		self.purpose = purpose
		self.depth = depth
		self.model = model		

		# Alpha : Minimum value for MAX found on current path
		# Beta  : Maximum value for MIN found on current path
		self.alpha = alpha
		self.beta = beta

		

		(self.final_situation, self.winner) = self.isFinalSituation()
	
		# Final configuration	
		if self.final_situation:
			if self.winner == self.initial_player:
				self.value = 200
			elif self.winner == 3 - self.initial_player:
				self.value = -200
			else:
				self.value = 0
		
		# Not final configuration
		else:
			# Generate subtree, and get value from children
			if self.depth < self.max_depth:
				self.generateSubtree()
			
				if self.purpose_array[self.purpose] == "Max" and len(self.child_nodes) > 0:
					self.value = -200 
					for child in self.child_nodes:
						if child.value > self.value:
							self.value = child.value

				elif self.purpose_array[self.purpose] == "Min" and len(self.child_nodes) > 0:
					self.value = 200 
					for child in self.child_nodes:
						if child.value < self.value:
							self.value = child.value

			# No children and not final configuration
			# Use neural network to estimate value
			else:
				original_matrix = copy.deepcopy(self.game.board_matrix)
	
		        	if self.initial_player == 2:
					for i in range(6):
						for j in range(7):
							self.game.board_matrix[i][j] = 3 - self.game.board_matrix[i][j] \
							if self.game.board_matrix[i][j] != '-' else '-'		
				
				nn_matrix = self.game.export_current_board()
				self.value = model(Variable(torch.Tensor([nn_matrix]))).data[0, 0]
			
				self.game = copy.deepcopy(original_matrix)

				
		# Debug
		if self.depth == 0:
			vls = []
			for c in self.child_nodes:
				vls.append(c.value)

			print vls
			print "Best: " + str(self.value)


	def generateSubtree(self):
		for col in range(7):
			if self.game.board_matrix[self.game.first_free_row[col]][col] == "-":
				new_game = copy.deepcopy(self.game)
				new_game.board_matrix[new_game.first_free_row[col]][col] = self.player
				
				new_game.count_player_cols[self.player][col] += 1
                        	new_game.count_player_rows[self.player][new_game.first_free_row[col]] += 1

                        	new_game.first_free_row[col]-=1
                        	new_game.piece_number[self.player] += 1

				child = MiniMaxNeuralNetworkTree (new_game, self.model, \
					initial_player = self.initial_player, player = (3-self.player), purpose = 1-self.purpose, \
					parent_move = col, depth = self.depth + 1)
				
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

