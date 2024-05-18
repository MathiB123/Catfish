import game
from game_design import *

p.init()
screen = p.display.set_mode((WIDTH, HEIGHT))
x = game.Game()
load_images()
screen.fill(p.Color("white"))
running = True
sqSelected = () #aucune case selectionné, (rangee, colonne)
playerClicks = []
human_turn = True

while running:
    for e in p.event.get():
        if e.type == p.QUIT:
            running = False
        elif e.type == p.KEYDOWN:
            if e.key == p.K_z and len(x.moves) != 0:
                x.undo_move()
        
        elif e.type == p.MOUSEBUTTONDOWN and human_turn: #quand on clique
            location = p.mouse.get_pos() #(x,y) de la souris
            col = location[0]//SQ_SIZE #la position en x divisée par la taille du carré
            row = 7 - location[1]//SQ_SIZE #la position en y
            if sqSelected == (row, col): #utilisateur a cliqué 2x à la même place
                sqSelected = () #clear la case choisie
                playerClicks = [] #clear les clicks du joueur
            else:
                sqSelected = (row, col) #la case selectionnée
                playerClicks.append(sqSelected) #append le clique
            if len(playerClicks) == 2:
                is_move_made, move = x.move_played(playerClicks[0], playerClicks[1])
                if is_move_made:
                    sqSelected = ()
                    playerClicks = []
                    #human_turn = False
                else:
                    playerClicks = [sqSelected]
        elif len(x.get_all_legal_moves()) == 0: #Si la partie a fini en checkmate
            print("Checkmate. Game Over!")
            running = False
        
        # elif not human_turn:
        #     move = random.choice(x.get_all_legal_moves())
        #     if move.is_en_passant_move:
        #         x.make_en_passant_move(move)
        #     elif move.is_castling_move:
        #         x.make_castling_move(move)
        #     else: 
        #         x.make_move(move)
        #     human_turn = True

    # Draw the chessboard on the screen
    drawBoard(screen)
    draw_pieces(screen, x)
    highlightSquares(screen, x, sqSelected)
    # Update the display
    p.display.flip()