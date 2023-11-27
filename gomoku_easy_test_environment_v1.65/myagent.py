import random, sys, time, copy, math
import gomoku
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

        self.finished = GmUtils.isWinningMove(last_move, gamestate[0])
        
    def fully_expanded(self):
        return len(self.children) is len(self.valid_moves)

    def calculateUCB(self):
        win_ratio = self.Q / self.N
        c = 1 / math.sqrt(2)
        res = win_ratio + c * math.sqrt(math.log2(self.parent.N) / self.N)
        return res

    def FindBestChild(self):
        best_child = random.choice(self.children)
        best_value = best_child.calculateUCB()
        for child in self.children:
            child_UCB = child.calculateUCB()
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
        print (state)
        max_time = (max_time_to_move / 1000) - 0.05
        start_time = time.perf_counter()
        time_elapsed = time.perf_counter() - start_time
        valid_moves = gomoku.valid_moves(state)
        root = treeNode(state, last_move, valid_move_list=valid_moves)
        while time_elapsed < max_time:
            n_rollouts = 100
            leaf = root.FindSpotToExpand()
            if self.black:
                for i in range(n_rollouts):
                    leaf.Rollout(GmGame.BLACK)
            else:
                for i in range(n_rollouts):
                    leaf.Rollout(GmGame.WHITE)
            time_elapsed = time.perf_counter() - start_time
        best_root_child = root.FindBestChild()
        return  best_root_child.last_move

    def id(self) -> str: # Done
        return "Ka Long Yang (1676436)"
    
    start_time = time.perf_counter()
    print(start_time)
    time.sleep(1.3)
    stop_time = time.perf_counter()
    print(stop_time)
    time.sleep(1.3)
    stop_time = time.perf_counter()
    print(stop_time)