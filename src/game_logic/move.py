### This file implements the Move class which stores info about a possible move. ###

class Move:
    def __init__(self, init_square : tuple[int, int], final_square : tuple[int, int], piece_tag : str, 
                 en_passant_square = (0,0), is_en_passant_move = False, is_castling_move = False, 
                 is_promotion = False):
        #Movements: (i,j) -> (i',j')
        self.init_square = init_square
        self.final_square = final_square
        
        #What piece is moved
        self.piece_tag = piece_tag

        #(0,0) if the move doesn't allow en passant on next move, else (x,y) where it's possible
        self.en_passant_square = en_passant_square
        #Is this move a capture en passant?  
        self.is_en_passant_move = is_en_passant_move

        #Is it a castling move?
        self.is_castling_move = is_castling_move
        
        #Does this move allow a promotion?
        self.is_promotion = is_promotion