from socket32 import create_new_socket
from game import Game, Player

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65433  # Port to listen on (non-privileged ports are > 1023)

def main():

    with create_new_socket() as s:
        # Bind socket to address and publish contact info
        s.bind(HOST, PORT)
        s.listen()
        print("Checkers server started. Listening on", (HOST, PORT))

        # Answer incoming connection
        conn2client, addr = s.accept()
        print('Connected by', addr)

        # Have each player maintain a Checkers state machine
        checkers = Game(Player.BLUE)

        with conn2client:
            while True:   # message processing loop
                message = conn2client.recv_move()
                if not message:  
                    break

                opp_piece, opp_move_list = message
                checkers.run_moves(checkers.opponent(), opp_piece, opp_move_list)
                if checkers.is_game_over():
                    break

                piece, move_list = checkers.run_player_turn()
                conn2client.send_move(piece, move_list)
                if checkers.is_game_over():
                    break
                
            print('Disconnected')

if __name__ == '__main__':
    main()

