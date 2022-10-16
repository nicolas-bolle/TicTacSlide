# Game and solver for TicTacSlide
# Basic pygame code modified from https://techvidvan.com/tutorials/python-game-project-tic-tac-toe/

import numpy as np
import pygame
import time
import pickle
from os.path import exists
import os

# For debugging
out1 = []
out2 = []
max_branch_length = 0
debug_counter = 0

WIN_IND = [([0,0,0], [0,1,2]), ([1,1,1], [0,1,2]), ([2,2,2], [0,1,2]), ([0,1,2], [0,0,0]), ([0,1,2], [1,1,1]), ([0,1,2], [2,2,2]), ([0,1,2], [0,1,2]), ([0,1,2], [2,1,0])]

class Game():
    """ A game engine for TicTacSlide
    """

    # Constants
    D = 400 # height/width
    B = 100 # height of the bottom bar
    BLACK = (0, 0, 0) # colors
    WHITE = (255, 255, 255)
    LINE = (10,10,10)
    WIN = (160,60,220)

    # Starts the game
    def __init__(self, moves):
        # Save the move dictionary
        self.moves = moves

        # Set some constants
        self.S = self.D/3 # Width of the squares
        self.IMG = self.S * 0.8 # Size of the X/O graphics
        self.OFFSET = self.IMG/2 # Offset to apply to get from the center of a square to the top left for the graphics

        # Initializing pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((self.D, self.D+self.B),0,32)
        pygame.display.set_caption("Tic Tac Toe")

        # Loading the images
        opening = pygame.image.load(os.path.join(__location__, 'tic tac opening.jpg'))
        x_img = pygame.image.load(os.path.join(__location__, 'x.png'))
        o_img = pygame.image.load(os.path.join(__location__, 'o.png'))

        # Resizing images
        self.x_img = pygame.transform.smoothscale(x_img, (self.IMG,self.IMG))
        self.o_img = pygame.transform.smoothscale(o_img, (self.IMG,self.IMG))
        self.opening = pygame.transform.smoothscale(opening, (self.D, self.D))
        
        # Run the load screen
        self.load_screen()
        
        # Run the main game until one of the inner loops breaks it
        big_loop = True
        while big_loop:
            # Go into the start screen loop
            big_loop = self.start_screen()

            # Go into the main loop
            if big_loop:
                big_loop = self.main()
        
        # End
        pygame.quit()

    # Create the loading screen and load optimal moves
    def load_screen(self):

        # Logo with a loading... text
        self.screen.blit(self.opening,(0,0))
        self.text("Loading...")
        pygame.display.update()
        time.sleep(0.5) # Lmao, there isn't anything to load; but I'll keep the load screen
        

    # Run the start screen
    def start_screen(self):
        pygame.display.update()
        # Logo with two buttons for player 1 or 2
        self.screen.fill(self.BLACK)
        self.screen.blit(self.opening,(0,0))
        pygame.draw.line(self.screen,self.WHITE,(self.D/2,self.D),(self.D/2, self.D+self.B),7)
        self.text("X", self.D/4, self.D+self.B/2)
        self.text("O", 3*self.D/4, self.D+self.B/2)
        pygame.display.update()
        
        # Loop until the player picks player 1 or 2
        loop = True
        big_loop = True
        while loop:
            for event in pygame.event.get():
                # User closes the game
                if event.type == pygame.QUIT:
                    loop = False
                    big_loop = False
                # User clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If they clicked one of the two buttons, start the game
                    x,y = pygame.mouse.get_pos()
                    if y > self.D:
                        if x < self.D/2:
                            self.human_player = 1
                        else:
                            self.human_player = 2
                        loop = False
        
        return big_loop

    # Run the main screen
    def main(self):

        # Create the board
        self.board = [[0]*3,[0]*3,[0]*3]
        self.draw_board()
        self.player = 1 # The player who is about to go

        # Number of pieces and whether we're listening for the second click
        self.n = 0
        self.first = False

        # If the AI has to go first, do that
        if self.human_player == 2:
            I1,I2 = self.AI()
            self.play(I1,I2)
        

        loop = True
        big_loop = True
        while loop:
            for event in pygame.event.get():
                # User closes the game
                if event.type == pygame.QUIT:
                    loop = False
                    big_loop = False
                # User clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Process the click
                    loop = self.click()
        
        return big_loop

    # Print a message to the bottom part of the screen
    def text(self, message, x=None, y=None):
        if not x:
            x = self.D / 2
        if not y:
            y = self.D + self.B/2
        font = pygame.font.Font(None, 30)
        text = font.render(message, 1, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y))
        self.screen.blit(text, text_rect)

    # Draw the tic tac toe board
    def draw_board(self):

        self.screen.fill(self.WHITE)

        # Drawing vertical lines
        pygame.draw.line(self.screen,self.LINE,(self.S,0),(self.S, self.D),7)
        pygame.draw.line(self.screen,self.LINE,(self.S*2,0),(self.S*2, self.D),7)
        # Drawing horizontal lines
        pygame.draw.line(self.screen,self.LINE,(0,self.S),(self.D, self.S),7)
        pygame.draw.line(self.screen,self.LINE,(0,self.S*2),(self.D, self.S*2),7)
        
        # self.BLACK bottom region
        self.screen.fill(self.BLACK, (0, self.D, self.D, self.B))
        
        pygame.display.update()

    # Returns the square that the AI would play
    def AI(self):
        code = Board.encode(self.board, self.player)
        ev, num, I1, I2 = self.moves[code]
        assert I1
        return I1, I2

    # "Plays" a move (and updates self.player, and number of pieces)
    def play(self,I1,I2):
        
        # The "new tile"
        i,j = I1
        self.board[i][j] = self.player
        x, y = self.ij2xy(i,j,True)
        if self.player == 1:
            self.screen.blit(self.x_img, (x,y))
        else:
            self.screen.blit(self.o_img, (x,y))
        
        # Possibly removing the "old tile", for the Slide phase
        if I2:
            i,j = I2
            self.board[i][j] = 0
            x, y = self.ij2xy(i,j,True)
            self.screen.fill(self.WHITE, (x, y, self.IMG, self.IMG))

        # Some variable updates
        self.player = 3 - self.player
        self.n = min(self.n + 1, 6)

        # Update visuals
        pygame.display.update()

    # Converts indices to a centered position
    # graphics=True for the graphics offset
    def ij2xy(self, i, j, graphics=False):
        x = i * self.S + self.S/2
        y = j * self.S + self.S/2
        if graphics:
            x -= self.OFFSET
            y -= self.OFFSET
        return x, y

    # Figures out if the user clicked a square
    # If they did, depending on the phase of the game either play that square or wait for the second click
    # Then have the AI play their square
    def click(self):

        x, y = pygame.mouse.get_pos()

        # Outside region
        if y > self.D:
            return True
        
        # The square clicked
        i = int(x/self.S)
        j = int(y/self.S)

        # Cases depending on the phase of the game
        if self.n < 6:
            # Clicked a taken square: move fails
            if self.board[i][j]:
                return True
            
            # Otherwise, set up the move coords
            I1 = (i,j)
            I2 = None
        else:
            # Listening for the first click
            if not self.first:
                # Clicked a square without our piece: move fails
                if self.board[i][j] != self.human_player:
                    return True
                
                # Otherwise, mark this as the first click (the tile to remove) and go to listen for the second one
                self.I2 = (i,j)
                self.first = True
                return True
            
            # Listening for the second click
            else:
                # Clicked a taken square: move fails
                if self.board[i][j]:
                    return True
                
                # Clicked on a square not adjacent to self.I1: move fails
                if abs(self.I2[0] - i) + abs(self.I2[1] - j) != 1:
                    return True
                
                # Otherwise, the move goes through! Set it up
                I1 = (i,j)
                I2 = self.I2
                self.first = False

        # Play our move
        self.play(I1,I2)
        if self.endQ():
            return False

        # Small pause for the human to process things with their TINY HUMAN BRAIN
        time.sleep(0.5)

        # Now it's the AI's turn
        I1,I2 = self.AI()
        self.play(I1,I2)
        if self.endQ():
            return False
        
        # Keep playing
        return True

    # See if the game ended
    # If it didn't return False
    # If it did, highlight the winning triple and tell the user, and after a short pause return True
    def endQ(self):
        win, I, J = Board.win_check(self.board)
        
        if win:
            # Line
            pygame.draw.line(self.screen,self.WIN,self.ij2xy(I[0],J[0]),self.ij2xy(I[2],J[2]),7)

            # Text
            if self.board[I[0]][J[0]] == self.human_player:
                self.text("You win~")
            else:
                self.text("You lose :P")
            
            pygame.display.update()
            time.sleep(2)
            
            return True
        
        # Otherwise, it hasn't ended
        return False


class Board():
    """The board, for generating the tree of moves and evaluating the positions
    """

    # Create the object with its board, player, number of existing pieces, and dictionary of optimal moves for evaluation
    def __init__(self, board, player, n):
        self.board = board
        self.player = player
        self.n = n
        
        # Our code for the dictionary
        self.code = Board.encode(self.board, self.player)
    
    # Function turning a board state into a dictionary key in some standardized way
    # Sidenote: does [][] indexing because the Game() object might have a non-numpy board
    @staticmethod
    def encode(board, player):
        # I'll essentially do a base 3 representation
        code = player
        multiplier = 3
        for i in range(3):
            for j in range(3):
                code += board[i][j] * multiplier
                multiplier *= 3
        return code
    
    # Helper function to say who wins: 1 for player 1, 2 for player 2, 0 if neither won yet
    @staticmethod
    def win_check(board):
        win = 0
        for I, J in WIN_IND:
            if board[I[0]][J[0]] and (board[I[0]][J[0]] == board[I[1]][J[1]] == board[I[2]][J[2]]):
                win = board[I[0]][J[0]]
                break
        return win, I, J

    # Evaluate the position of this board by spawning its children and recursively evaluating their positions
    # Records the result in the given dictionary for tracking optimal moves
    # Returns a tuple (eval, num_moves, (i1, j1), (i2, j2)) giving the evaluation and optimal move, where a piece is place in the former and one is possibly removed from the latter
    # When visiting a node (board state) for the first time, set the dictionary value to (0, 0, None, None) so that if we loop back we get a draw
    # BUT, doubt previous evaluations for draws that are not in our branch
    def evaluate(self, moves, branch):
        
        #if self.code == 40253:
        #    global out1
        #    out1.append(self)
        #    print(self.code)

        #if self.code == 14008:
        #    global out2
        #    out2.append(self)
        #    print(self.code)

        # If we've already evaluated it...
        if self.code in moves:
            # Trust a non-draw evaluation, or if it's already in the branch
            # FIXME instead of the branch idea, just doing a random chance to trust
            if moves[self.code][0] or self.code in branch or np.random.uniform() < 0.5:
                return moves[self.code]
        # If we didn't already evaluate it, then we haven't checked if it's a win state yet
        # You can show by hand that stalemates don't exist: every position where player 1 would not have a move is already a win for one of the players
        else:
            # Check if it's a win state
            w, _, _ = Board.win_check(self.board)
            if w:
                moves[self.code] = (w, 0, None, None)
                return moves[self.code]
        
            # Otherwise, set its dictionary value to (0, 0, None, None) as we're passing through for the first time
            moves[self.code] = (0, 0, None, None)
        
        # Now we'll go on to check its children

        # Mark it as visited in our branch
        branch[self.code] = None

        # Print the longest branch length found so far
        #global max_branch_length, debug_counter
        #if len(branch) > max_branch_length:
        #    max_branch_length = len(branch)
        #    print('Branch len:', max_branch_length)
        #debug_counter += 1
        #if debug_counter == 10000:
        #    debug_counter = 0
        #    # Count the number of state evaluations that are non-draw, and the number of states
        #    print(len([1 for t in moves.values() if t[0]]))
        #    print(len(moves))
        #    print(' ')

        # This will be a list of the (eval, num_moves, (i1, j1), (i2, j2)) tuples we can choose from here
        self.evals = []

        # Case 1: TicTacToe phase
        if self.n < 6:
            # Loop over locations that don't have pieces
            for i,j in np.argwhere(self.board == 0):
                # The new board state
                new_board = self.board.copy()
                new_board[i,j] = self.player
                
                # Create and evaluate, turning its return into what that move would achieve for us
                ev, num, _, _ = Board(new_board, 3-self.player, self.n + 1).evaluate(moves, branch)
                self.evals.append((ev, num+1, (i,j), None))
        # Case 2: TicTacSlide phase
        else:
            # The locations where my pieces are, and where there are no pieces
            mine  = np.argwhere(self.board == self.player)
            empty = np.argwhere(self.board == 0)

            # Match these up, as pairs of tuples
            possible_moves = [(tuple(I1),tuple(I2)) for I1 in empty for I2 in mine if np.sum(np.abs(I1-I2)) == 1]

            # To catch an edge case that I think shouldn't happen
            assert len(possible_moves) > 0

            # Loop over those possible moves
            for I1,I2 in possible_moves:
                # The new board state
                new_board = self.board.copy()
                new_board[I1] = self.player
                new_board[I2] = 0
                
                # Create and evaluate, turning its return into what that move would achieve for us
                ev, num, _, _ = Board(new_board, 3-self.player, self.n).evaluate(moves, branch)
                self.evals.append((ev, num+1, I1, I2))
        
        # Now pick the best move, according to the values of self.children
        # Sort: first level by the player who wins, second level by the number of moves to reach the end
        get_priority = lambda t : (self.player_priority(t[0]), t[1])
        self.evals.sort(key=get_priority)
        moves[self.code] = self.evals[0]

        #if self.code in [40253, 14008]:
        #    print("set", self.code)

        # Finally, unmark us as in the branch as we return upwards
        del branch[self.code]

        return moves[self.code]
    
    # Helper function that assigns a numeric value to a player number to aid in sorting
    # If the player number is mine, 0; if it's a draw, 1; if it's the other player, 2
    # That way, me winning is prioritized
    def player_priority(self, p):
        if p == self.player:
            return 0
        elif not p:
            return 1
        else:
            return 2
    
    # Visualize the board
    def __str__(self):
        # Constants to help build things
        space = "     |     |     "
        line = "_____|_____|_____"
        side = "  "
        mid = "  |  "
        new = "\n"
        
        # Build the string
        string = ""
        if self.player == 1:
            string += 'x'
        else:
            string += 'o'
        string += ' to move' + new
        string += space + new
        string += side + self._char(0,0) + mid + self._char(0,1) + mid + self._char(0,2) + side + new
        string += line + new
        string += space + new
        string += side + self._char(1,0) + mid + self._char(1,1) + mid + self._char(1,2) + side + new
        string += line + new
        string += space + new
        string += side + self._char(2,0) + mid + self._char(2,1) + mid + self._char(2,2) + side + new
        string += space + new
        
        # Return
        return string
    
    # Helper function to find the character to print for a given square
    def _char(self, i, j):
        num = self.board[i,j]
        if num == 1:
            return 'x'
        elif num == 2:
            return 'o'
        else:
            return ' '


# Runs the TicTacSlide game
if __name__ == "__main__":
    # Using code from here to get the current path https://stackoverflow.com/a/4060259
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    
    # First makes sure the optimal moves are precomputed
    filename = os.path.join(__location__, 'TicTacSlide.pkl')
    if exists(filename):
        with open(filename, "rb") as file:
            moves = pickle.load(file)
    # Otherwise, generate them (and save them!)
    else:
        # Create the starting board
        B = Board(np.zeros((3,3), dtype=np.int8), 1, 0)
        
        # Run the board's method to compute its optimal moves
        moves = {}
        branch = {}
        B.evaluate(moves, branch)
        
        # Pickle for future use
        with open(filename, "wb") as file:
            pickle.dump(moves, file)
    
    # Now run the game with this dictionary of moves
    # How the dictionary is formatted:
    # - The keys are board states converted to integers, using Board()'s encode() function
    # - The value is a tuple (eval, (i1,j1), (i2,j2)) giving the board evaluation and the optimal move it chose
    # - 1 = player 1, 2 = player 2, 0 = draw; indices are in [0,1,2]
    # - During the TicTacToe phase, the 3 element of the tuple is None
    game = Game(moves)