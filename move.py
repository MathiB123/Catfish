class Move:
    def __init__(self, init_square, final_square, bb_piece, is_castling_move = False, en_passant_possible = False, en_passant_square = (0,0), is_en_passant_move = False, is_promotion = False):
        self.init_square = init_square
        self.final_square = final_square
        self.bb_piece = bb_piece

        self.en_passant_possible = en_passant_possible
        self.en_passant_square = en_passant_square
        self.is_en_passant_move = is_en_passant_move

        self.is_castling_move = is_castling_move
        
        self.is_promotion = is_promotion

        self.moveID = self.init_square[0] * 1000 + self.init_square[1] * 100 + self.final_square[0] * 10 + self.final_square[1]

    def __eq__(self, other): # = operator for the Move class
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False