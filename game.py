from enum import Enum
from typing import Tuple, List

class Player(Enum):
    RED = 1
    BLACK = 2

Coordinate = Tuple[int, int]
Piece = Coordinate
Moves = List[Coordinate]

BOARD_SIZE = 8
RED_CIRCLE = u'\033[91m\u25CF\033[0m'
RED_HEART = u'\033[91m\u2665\033[0m'
BLACK_CIRCLE = u'\033[94m\u25CF\033[0m'
BLACK_HEART = u'\033[94m\u2665\033[0m'
BLACK_SQUARE = u'\u25A0'
WHITE_SQUARE = u'\u25A1' 


class Game:
    def __init__(self, curr_player: Player):
        self.size = BOARD_SIZE
        self.curr_player = curr_player

        # Instantiate red's pieces
        self.red_pieces = []
        self.red_kings = []
        for i in range(0, 3):
            for j in range(self.size):
                if (i+j) % 2 == 0:
                    self.red_pieces.append((i,j))

        # Instantiate black's pieces
        self.black_pieces = []
        self.black_kings = []
        for i in range(self.size-3, self.size):
            for j in range(self.size):
                if (i+j) % 2 == 0:
                    self.black_pieces.append((i, j))

    def opponent(self) -> Player:
        """
        Returns:
            The opponent player with context of the game's current player.
        """
        return Player.RED if self.curr_player == Player.BLACK else Player.BLACK

    def get_pieces(self, player: Player):
        """
        Gets the pieces with the context of the player.
        """
        if player == Player.RED:
            pieces = self.red_pieces
            kings = self.red_kings
            opponent_pieces = self.black_pieces
            opponent_kings = self.black_kings
        else:
            pieces = self.black_pieces
            kings = self.black_kings
            opponent_pieces = self.red_pieces
            opponent_kings = self.red_kings
        
        return pieces, kings, opponent_pieces, opponent_kings

    def get_coordinate(self) -> Coordinate:
        """
        Loops for user input until a valid coordinate is inputted.
        
        Returns: 
            A coordinate tuple (x, y).
        """
        while True:
            input_coord = input('Input a coordinate in "x,y" format: ')
            try:
                tup = tuple(map(int, input_coord.split(',')))
                if len(tup) != 2:
                    print('Invalid input format. Please provide coordinates in "x,y" form.')
                    continue
                return tup
            except ValueError:
                print('Invalid input format. Please provide coordinates in "x,y" form.')

    def calculate_all_moves(self, piece: Piece) -> Tuple[Moves, Moves]:
        """
        Calculates all possible moves for a piece given the current player.

        Returns: 
            normal_moves, jump_moves (both lists of coordinates)
        """
        pieces, kings, opp_pieces, opp_kings = self.get_pieces(self.curr_player)
        total_pieces = pieces + kings + opp_pieces + opp_kings

        normal_moves, jump_moves = [], []
        
        if piece in kings:
            # Kings can move in all four diagonal directions
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] 
        else:
            directions = [(1, 1), (1, -1)] if self.curr_player == Player.RED else [(-1, 1), (-1, -1)]

        # Calculate normal moves
        for dx, dy in directions:
            move = piece[0] + dx, piece[1] + dy

            within_bounds = (0 <= move[0] < self.size) and (0 <= move[1] < self.size)
            is_empty_space = move not in total_pieces

            if within_bounds and is_empty_space:
                normal_moves.append(move)

        # Calculate jump moves
        for dx, dy in directions:
            jump = piece[0] + 2 * dx, piece[1] + 2 * dy
            mid = piece[0] + dx, piece[1] + dy

            within_bounds = (0 <= jump[0] < self.size) and (0 <= jump[1] < self.size)
            is_empty_space = jump not in total_pieces 
            jumped_opponent = (mid in opp_pieces) or (mid in opp_kings)

            if within_bounds and is_empty_space and jumped_opponent:
                jump_moves.append(jump)

        return normal_moves, jump_moves
    
    def handle_jump_sequence(self, pieces: List[Piece]) -> Tuple[Piece, Moves]:
        """
        Handles a jumping sequence. Accounts for double jumps

        Args:
            pieces: a list of pieces that can be jumped.

        Returns: 
            initial_piece: The first piece in the jump
            move_list: The moves that piece takes
        """

        # Pick the piece you want to jump with
        if len(pieces) > 1:
            print(f"A jump exists for multiple pieces. Pick one: {pieces}!")
            initial_piece = self.get_coordinate()
            while initial_piece not in pieces:
                print("Invalid piece. Please try again.")
                initial_piece = self.get_coordinate()
        else:
            initial_piece = pieces.pop(0)
            print(f"A jump exists for {initial_piece}!")

        curr_piece = initial_piece
        move_list = []
        _, curr_jumps = self.calculate_all_moves(curr_piece)

        # Loop jumps until no more jumps exist
        while True:
            print("Current possible jumps: ", curr_jumps)
            move = self.get_coordinate()
            while move not in curr_jumps:
                print("Invalid jump. Please try again.")
                move = self.get_coordinate()

            move_list.append(move)
            self.run_moves(self.curr_player, curr_piece, [move])  
            curr_piece = move

            # Check for further jumps from the new position
            _, curr_jumps = self.calculate_all_moves(curr_piece)

            if not curr_jumps: # no more jumps exist
                break

        return initial_piece, move_list

    def run_player_turn(self) -> Tuple[Piece, Moves]:
        """
        Runs current player's turn. Generates a move list to send over the wire.

        Returns: piece, move_list
        """
        pieces = self.get_pieces(self.curr_player)[0]
        piece, move_list = None, []

        # If a jump exists, it is a rule that you must take it
        potential_jumps = [] # pieces that contain potential jumps
        for piece in pieces:
            _, jump_moves = self.calculate_all_moves(piece)
            if jump_moves:
                potential_jumps.append(piece)

        if potential_jumps:
            piece, move_list = self.handle_jump_sequence(potential_jumps)
            return piece, move_list

        print(f'Please pick a piece to move Player {self.curr_player}')

        # Loop until we get a valid piece
        while True:
            piece = self.get_coordinate()
            # Calculate all possible moves that piece can make
            normal_moves, jump_moves = self.calculate_all_moves(piece)

            if piece in pieces:
                if normal_moves:
                    break
                else:
                    print('Piece has no valid moves. Please try again.')
            else:
                print('Invalid piece. Please try again.')

        # Loop until we get a valid move 
        print(f'Please pick a move for {piece}')
        while True:
            move = self.get_coordinate()
            if move in normal_moves:
                move_list.append(move)
                self.run_moves(self.curr_player, piece, [move])
                break
            else:
                print('Invalid move. Please try again.')

        return piece, move_list
    
    def is_jump(self, piece: Coordinate, move: Coordinate) -> bool:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] 
        for dx, dy in directions:
            potential_move = (piece[0] + 2 * dx, piece[1] + 2 * dy)
            if potential_move == move:
                return True
        return False

    def run_moves(self, player: Player, piece: Coordinate, moves: Moves):
        pieces, kings, opp_pieces, opp_kings = self.get_pieces(player)

        for move in moves:
            pieces.remove(piece)
            pieces.append(move)
            if piece in kings: # update our kings
                kings.remove(piece)
                kings.append(move)

            if self.is_jump(piece, move):
                jumped_piece = ((piece[0] + move[0]) // 2, (piece[1] + move[1]) // 2)
                opp_pieces.remove(jumped_piece)
                if jumped_piece in opp_kings: # update opp kings
                    opp_kings.remove(jumped_piece)
                piece = move # next piece in jump

            # If piece is in the back line.. promote it
            if piece[0] == 0 and player == Player.BLACK:
                print('making black king')
                kings.append(piece)
            elif piece[0] == 7 and player == Player.RED:
                print('making red king')
                kings.append(piece)
            
            # Print the board with every move
            self.print_board()
            
    def is_game_over(self) -> bool:
        if not self.red_pieces:
            print("Black wins!")
            return True
        
        if not self.black_pieces:
            print("Red wins!")
            return True

        return False

    def print_board(self):
        """
        Prints the checkers board. 
        """
        # Print the top numbers of the board
        print('    ', end = '')
        for i in range(self.size):
            print(i, end = ' ')
        print()

        # Print the top bar
        print('   ', end = '')
        for i in range(self.size):
            print('--', end = '')
        print()
        
        for i in range(self.size):
            print(f'{i} | ', end ='') # Left-side numbers
            for j in range(self.size):
                coord = (i, j)

                # Player RED pieces
                if coord in self.red_kings:
                    print(RED_HEART, end=' ')
                elif coord in self.red_pieces:
                    print(RED_CIRCLE, end=' ')
                
                # Player BLACK pieces
                elif coord in self.black_kings:
                    print(BLACK_HEART, end=' ')
                elif coord in self.black_pieces:
                    print(BLACK_CIRCLE, end=' ')

                # Empty spaces
                else:
                    if (i+j) % 2 == 0:
                        print(BLACK_SQUARE, end=' ')
                    else:
                        print(WHITE_SQUARE, end=' ')
            print()