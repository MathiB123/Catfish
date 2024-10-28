### This file implements anything related to the display of the board/pieces in a window. ###

import pygame as p

#Useful constants
WIDTH = HEIGHT = 700
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION 
PIECES = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
IMAGES = {}


def load_images() -> None:
    """Loads pieces from the "Images" folder on the board.

    """
    for piece in PIECES:
        IMAGES[piece] = p.transform.scale(p.image.load("src/game_design/Images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def drawBoard(screen) -> None:
    """Draws the squares on a Pygame display.

    Args:
        screen (Pygame display): The pygame display where to draw the squares.
    """
    colors = [p.Color("white"), p.Color("burlywood3")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, bitboards : dict, white_to_move : bool) -> None: 
    """Draws the pieces on a Pygame display. 

    Args:
        screen (Pygame display): The pygame display where to draw the pieces.
        bitboaards (dict): The current chess game.
        white_to_move (bool): Whose turn it is.
    """
    for piece in PIECES:
        bitboard = bitboards[piece]
        #On what squares are the pieces
        positions = []
        for index in range(bitboard.bit_length()):
            if (bitboard >> index) & 1:
                i,j = divmod(int(index), 8)
                positions.append((index, i, j))
        #Drawing the pieces
        if white_to_move:
            for position in positions:
                screen.blit(IMAGES[piece], p.Rect(position[2]*SQ_SIZE, (7-position[1])*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        else:
            for position in positions:
                screen.blit(IMAGES[piece], p.Rect((7-position[2])*SQ_SIZE, position[1]*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, white_to_move : bool, sqSelected : tuple[int, int], legal_moves : list) -> None:
    """Highlights the selected square/piece in blue and shows the legal moves in yellow on the screen.

    Args:
        screen (Pygame display): The pygame display where the board is.
        white_to_move (bool): Whose turn it is.
        sqSelected (tuple[int, int]): (x,y) position clicked by the player.
        legal_moves (list): All the legal moves in the current position.
    """
    if sqSelected != ():
        #Highlighting the selected square
        r, c = sqSelected
        s = p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100) 
        s.fill(p.Color('blue'))
        screen.blit(s,(c*SQ_SIZE, (7-r)*SQ_SIZE)) if white_to_move else screen.blit(s,((7-c)*SQ_SIZE, r*SQ_SIZE)) 
        s.fill(p.Color('yellow'))

        #Showing the legal moves
        if white_to_move:
            for move in legal_moves:
                if move.init_square[0] == r and move.init_square[1] == c:
                    screen.blit(s, (SQ_SIZE*move.final_square[1], SQ_SIZE*(7-move.final_square[0])))
        else:
            for move in legal_moves:
                if move.init_square[0] == r and move.init_square[1] == c:
                    screen.blit(s, (SQ_SIZE*(7-move.final_square[1]), SQ_SIZE*move.final_square[0]))