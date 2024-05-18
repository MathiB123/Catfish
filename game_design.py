import pygame as p


WIDTH = HEIGHT = 700 #400 pour meilleure résolution 
DIMENSION = 8 
SQ_SIZE = HEIGHT // DIMENSION # "//" est l'opérateur pour la divsion entière 
IMAGES = {}


def load_images() -> None:
    """Loads pieces from the "Images" folder in the game.

    """
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


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


def draw_pieces(screen, game_bitboard) -> None: 
    """Draws the pieces on a Pygame display. 

    Args:
        screen (Pygame display): The pygame display where to draw the pieces.
        game_bitboard (Game): The current chess game.
    """
    white_pieces = game_bitboard.list_white_bitboards
    black_pieces = game_bitboard.list_black_bitboards
    pieces = white_pieces + black_pieces
    for piece in pieces:
        positions = game_bitboard.find_indices_of_set_bits(piece)
        for position in positions:
            screen.blit(IMAGES[piece[1]], p.Rect(position[2]*SQ_SIZE, (7-position[1])*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        s = p.Surface((SQ_SIZE,SQ_SIZE))
        s.set_alpha(100) 
        s.fill(p.Color('blue'))
        screen.blit(s,(c*SQ_SIZE, (7-r)*SQ_SIZE))
        s.fill(p.Color('yellow'))
        validMoves = gs.get_all_legal_moves()
        for move in validMoves:
            if move.init_square[0] == r and move.init_square[1] == c:
                screen.blit(s, (SQ_SIZE*move.final_square[1], SQ_SIZE*(7-move.final_square[0])))