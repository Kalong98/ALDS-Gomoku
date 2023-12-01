import random, sys, time, copy, math
import gomoku
import numpy as np
from GmUtils import GmUtils
from GmGameRules import GmGameRules
from GmGame import GmGame


class treeNode:
    def __init__(self, gamestate: gomoku.GameState, last_move = None, parentNode = None, valid_move_list = None):
        """Constructor tree node"""
        self.gamestate = gamestate
        self.last_move = last_move
        self.parent = parentNode
        self.valid_moves = valid_move_list
        
        self.children = []
        self.visited = []
        self.Q = 0  # number of wins
        self.N = 0  # number of visits
        if (last_move != ()):
            self.finished = GmUtils.isWinningMove(last_move, gamestate[0])
        else:
            self.finished = False
        
    def fully_expanded(self):
        return len(self.children) == len(self.valid_moves)

    def calculateUCT(self):
        if self.N > 0:
            win_ratio = self.Q / self.N
            c = 1 / math.sqrt(2)
            res = win_ratio + (c * (math.sqrt(math.log2(self.parent.N) / self.N)))
            return res
        else:
            return 0

    def FindBestChild(self):
        best_child = random.choice(self.children)
        best_value = best_child.calculateUCT()
        for child in self.children:
            child_UCB = child.calculateUCT()
            if child_UCB > best_value:
                best_value = child_UCB
                best_child = child
        return best_child

    def FindSpotToExpand(self) -> 'treeNode': 
        if self.finished:
            return self
        elif not self.fully_expanded():
            move_to_do = random.choice(self.valid_moves)
            new_game_state = gomoku.move(self.gamestate, move_to_do)[2]
            new_valid_moves = copy.deepcopy(self.valid_moves)
            new_valid_moves.remove(move_to_do)
            new_child = treeNode(
                new_game_state, last_move=move_to_do, parentNode=self, valid_move_list=new_valid_moves
            )
            self.children.append(new_child)
            return new_child
        else:
            best_child = self.FindBestChild()
            return best_child.FindSpotToExpand()
    
    def Rollout(self, player):
        board = self.gamestate[0]
        move = self.last_move
        win = gomoku.check_win(board, move)
        if win: # if last move is a winning move
            if board[move[0]][move[1]] == player:
                self.process_result(1)
            else:
                self.process_result(-1)
        elif self.finished: # finished but no winner
                self.process_result(0)
        moves = copy.deepcopy(self.valid_moves)
        random.shuffle(moves)
        new_state = self.gamestate
        for move in moves:
            valid, win, game_state = gomoku.move(new_state, move)
            board = game_state[0]
            if win: # if last move wins the game
                if board[move[0]][move[1]] == player: # if player win return 1
                    self.process_result(1)
                else: #if player loses return -1
                    self.process_result(-1)
            elif GmGame.isBoardFull(board): # if board is full and no winners (tie)
                self.process_result(0)
    
    def process_result(self, rollout_result):
        # then we increase Q by the score, and N by 1
        self.Q += rollout_result
        self.N += 1
        # and do the same, recursively, for its ancestors
        if self.parent is not None:
            self.parent.process_result(rollout_result)
            
class SupremePlayer:
    def __init__(self, black_: bool = True): # Done
        """Constructor for the player."""
        self.black = black_

    def new_game(self, black_: bool): # Done
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_

    def move(self, state: gomoku.GameState, last_move: gomoku.Move, max_time_to_move: int = 1000) -> gomoku.Move:
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """
        max_time = (max_time_to_move / 1000) - 0.2
        start_time = time.perf_counter()
        time_elapsed = time.perf_counter() - start_time
        valid_moves = gomoku.valid_moves(state)
        # if there is only one available move (start)
        if len(valid_moves) == 1:
            return valid_moves[0]
        # check for winning move
        player = 0
        winning_move = None
        print(state[0])
        if self.black:
            player = GmGame.BLACK
        else:
            player = GmGame.WHITE
        winning_move = self.check_for_winning_move(state, player)
        if winning_move is not None:
            # print(f'own winning move {winning_move}')
            print(f'time_elapsed: {time_elapsed}')
            return winning_move
        # check and blocks opponent winning move
        if self.black:
            player = GmGame.WHITE
        else:
            player = GmGame.BLACK
        winning_move = self.check_for_winning_move(state, player)
        if winning_move is not None:
            # print(f'enemy winning move {winning_move}')
            print(f'time_elapsed: {time_elapsed}')
            return winning_move
        # use MCTS if no easy move
        root = treeNode(state, last_move, valid_move_list=valid_moves)
        n_rollouts = 50
        while time_elapsed < max_time:
            leaf = root.FindSpotToExpand()
            if self.black:
                for i in range(n_rollouts):
                    leaf.Rollout(GmGame.BLACK)
            else:
                for i in range(n_rollouts):
                    leaf.Rollout(GmGame.WHITE)
            time_elapsed = time.perf_counter() - start_time
        best_root_child = root.FindBestChild()
        print(f'time_elapsed: {time_elapsed}')
        return best_root_child.last_move

    def id(self) -> str: # Done
        return "Ka Long Yang (1676436)"
    
    def check_for_winning_move(self, state: gomoku.GameState, player):
        board = state[0]
        bsize = np.shape(state[0])[0] - 1
        # check horizontal
        winningmove = self.check_for_winning_move_hor(board, bsize, player)
        if winningmove is not None:
            # print(board)
            # print(f'winningmove hor: {winningmove}')
            return winningmove
        winningmove = self.check_for_winning_move_vert(board, bsize, player)
        if winningmove is not None:
            # print(board)
            # print(f'winningmove vert: {winningmove}')
            return winningmove
        winningmove = self.check_for_winning_move_diag(board, bsize, player)
        if winningmove is not None:
            # print(board)
            # print(f'winningmove diag: {winningmove}')
            return winningmove
        return None
        
    def check_for_winning_move_hor(self, board, bsize, player):
        for row in range(bsize):
            for col in range(bsize):
                in_row = 0
                empty_count = 0
                empty_space = ()
                if col + 4 <= bsize:
                    for i in range(5):
                        if board[row][col+i] == player:
                            in_row += 1
                        elif board[row][col+i] != 0: # spot taken by opponent
                            break
                        else:
                            empty_count += 1
                            empty_space = (row, col+i)
                            if empty_count > 1:
                                break
                    if in_row == 4 and empty_count == 1:
                        return empty_space
        return None
    
    def check_for_winning_move_vert(self, board, bsize, player):
        for col in range(bsize):
            for row in range(bsize):
                in_row = 0
                empty_count = 0
                empty_space = ()
                if row + 4 <= bsize:
                    for i in range(5):
                        if board[row+i][col] == player:
                            in_row += 1
                        elif board[row+i][col] != 0:
                            break
                        else:
                            empty_count += 1
                            empty_space = (row+i, col)
                            if empty_count > 1:
                                break
                    if in_row == 4 and empty_count == 1:
                        return empty_space
        return None
    
    def check_for_winning_move_diag(self, board, bsize, player):
        # check from top left to bottom right
        for row in range(bsize):
            for col in range(bsize):
                in_row = 0
                empty_count = 0
                empty_space = ()
                if row + 4 <= bsize and col + 4 <= bsize:
                    for i in range(5):
                        if board[row+i][col+i] == player:
                            in_row += 1
                        elif board[row+i][col+i] != 0:
                            break
                        else:
                            empty_count += 1
                            empty_space = (row+i, col+i)
                            if empty_count > 1:
                                break
                    if in_row == 4 and empty_count == 1:
                        return empty_space
        # check from bottom left to top right
        for row in range(bsize, 0, -1):
            for col in range(bsize, 0, -1):
                in_row = 0
                empty_count = 0
                empty_space = ()
                # check if it stays in a positive index
                if row - 4 >= 0 and col - 4 >= 0:
                    for i in range(5):
                        if board[row-i][col-i] == player:
                            in_row += 1
                        elif board[row-i][col-i] != 0:
                            break
                        else:
                            empty_count += 1
                            empty_space = (row-i, col-i)
                            if empty_count > 1:
                                break
                    if in_row == 4 and empty_count == 1:
                        return empty_space
        return None

    # start_time = time.perf_counter()
    # print(start_time)
    # time.sleep(1.3)
    # stop_time = time.perf_counter()
    # print(stop_time)
    # time.sleep(1.3)
    # stop_time = time.perf_counter()
    # print(stop_time)