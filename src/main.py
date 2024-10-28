from game_design.game_design import * 
from game_logic.game_state import Game
from game_logic.move_generation import get_all_legal_moves

p.init()
screen = p.display.set_mode((WIDTH, HEIGHT))
x = Game()
load_images()
screen.fill(p.Color("white"))
running = True
sqSelected = ()
playerClicks = []
legal_moves = []

while running:
    for e in p.event.get():
        if e.type == p.QUIT: #Quit the game
            running = False

        elif e.type == p.KEYDOWN: #To undo a move
            if e.key == p.K_z and len(x.moves) != 0:
                x.undo_move()
                sqSelected = ()
                playerClicks = []
                legal_moves = []
        
        elif e.type == p.MOUSEBUTTONDOWN:
            location = p.mouse.get_pos() #(x,y) move click location

            if x.white_to_move:
                col = location[0]//SQ_SIZE
                row = 7 - location[1]//SQ_SIZE 
            else:
                col = 7 - location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                
            if sqSelected == (row, col): #User clicked twice on the same square
                sqSelected = ()
                playerClicks = [] 
            else:
                sqSelected = (row, col)
                playerClicks.append(sqSelected)
                if len(playerClicks) != 2 and len(legal_moves) == 0:
                    legal_moves = get_all_legal_moves(x)

            if len(playerClicks) == 2: #A move made by the user
                move_made = x.make_legal_move(playerClicks[0], playerClicks[1], legal_moves)
                if move_made:
                    sqSelected = ()
                    playerClicks = []
                    legal_moves = []
                else:
                    playerClicks = [sqSelected]

            elif len(legal_moves) == 0: #If the game is over (Checkmate)
                print("Checkmate. Game Over!")
                running = False

    #Draw the chessboard on the screen
    drawBoard(screen)
    draw_pieces(screen, x.bitboards, x.white_to_move)

    #Highlight squares and possible moves
    highlightSquares(screen, x.white_to_move, sqSelected, legal_moves)
    
    #Update the display
    p.display.flip()