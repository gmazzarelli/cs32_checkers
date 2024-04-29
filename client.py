### chap05/guess-client.py
from socket32 import create_new_socket
from game import Game, Player

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65433        # The port used by the server

def main():
    print('## Welcome to Checkers! ##')

    with create_new_socket() as s:
        s.connect(HOST, PORT)

        # Have each player maintain a Checkers state machine
        checkers = Game(Player.RED)
        checkers.print_board()
    
        while True:   # message processing loop
            piece, move_list = checkers.run_player_turn()
            if checkers.is_game_over():
                break

            s.send_move(piece, move_list)

            message = s.recv_move()
            if not message:  
                break

            opp_piece, opp_move_list = message
            checkers.run_moves(checkers.opponent(), opp_piece, opp_move_list)
            if checkers.is_game_over():
                break

        print('Disconnected')

if __name__ == '__main__':
    main()
