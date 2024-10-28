### This file implements the Game class which is used to store information about the current chess game. ###

from game_logic.move import Move

class Game:
    def __init__(self):
        #From white's perspective:
        #Bottom left square has index 0, bottom right square has index 7, top left square has index 56, top square has index 63.
        #+1 to a square's index when going right and +8 when going up.
        self.bitboards = {"wP": 65280, "wN": 66, "wB": 36, "wR": 129, "wQ": 8, "wK": 16,
                          "bP": 65280 << 40, "bN": 66 << 56, "bB": 36 << 56, "bR": 129 << 56, "bQ": 8 << 56, "bK": 16 << 56,
                          "white": 65535, "black": 65535 << 48, "game": 65535 + (65535 << 48)}

        #Whose turn it is
        self.white_to_move = True

        #En passant info
        self.en_passant_square = [(0,0)]

        #Castling info
        self.wk_can_kingside_castle = [True]
        self.bk_can_kingside_castle = [True]
        self.wk_can_queenside_castle = [True]
        self.bk_can_queenside_castle = [True]

        #Other useful info
        self.moves = []
        self.captures = []

    def update_color_and_game_bitboard(self) -> None:
        """Updates self.bitboards["white"/"black"/"game"].
        """
        white_piece_tags = ["wP", "wN", "wB", "wR", "wQ", "wK"]
        black_piece_tags = ["bP", "bN", "bB", "bR", "bQ", "bK"]

        new_white_bitboard, new_black_bitboard = 0, 0
        for piece_tags in zip(white_piece_tags, black_piece_tags):
            new_white_bitboard += self.bitboards[piece_tags[0]]
            new_black_bitboard += self.bitboards[piece_tags[1]]

        self.bitboards["white"] = new_white_bitboard
        self.bitboards["black"] = new_black_bitboard
        self.bitboards["game"] = new_white_bitboard + new_black_bitboard 


    def make_regular_move(self, move : Move) -> None:
        """Updates the game's attributes to make a regular move.

        Args:
            move (Move): The legal move that was played.
        """
        #Updating the bitboard of the piece that is moved
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        self.bitboards[move.piece_tag] ^= mask       

        #Change the bitboard of a captured if the move is a capture
        color_piece_tags = ["bP", "bN", "bB", "bR", "bQ", "bK"] if self.white_to_move else ["wP", "wN", "wB", "wR", "wQ", "wK"]
        capture = None
        for piece_tag in color_piece_tags:
            if self.bitboards[piece_tag] & (1 << final_index):
                self.bitboards[piece_tag] ^= (1 << final_index)
                capture = piece_tag
                break
        self.captures.append(capture)

        #Update white, black and game bitboard
        self.update_color_and_game_bitboard()

        #Change en passant conditions
        self.en_passant_square.append(move.en_passant_square)

        #Update castling info
        #Can't castle if we move a rook/king or if a rook is captured or if castling wasn't available before 
        if self.wk_can_kingside_castle[-1] and (self.bitboards["wR"] & 128) and (self.bitboards["wK"] == 16):
            self.wk_can_kingside_castle.append(True)
        else:
            self.wk_can_kingside_castle.append(False)
        if self.wk_can_queenside_castle[-1] and (self.bitboards["wR"] & 1) and (self.bitboards["wK"] == 16):
            self.wk_can_queenside_castle.append(True)
        else:
            self.wk_can_queenside_castle.append(False)
        if self.bk_can_kingside_castle[-1] and (self.bitboards["bR"] & (128 << 56)) and (self.bitboards["bK"] == (16 << 56)):
            self.bk_can_kingside_castle.append(True)
        else:
            self.bk_can_kingside_castle.append(False)
        if self.bk_can_queenside_castle[-1] and (self.bitboards["bR"] & (1 << 56)) and (self.bitboards["bK"] == (16 << 56)):
            self.bk_can_queenside_castle.append(True)
        else:
            self.bk_can_queenside_castle.append(False)

        #Change turn
        self.white_to_move = not self.white_to_move


    def make_en_passant_move(self, move : Move) -> None:
        """Updates the game's attributes to make an en passant move.

        Args:
            move (Move): The legal move that was played.
        """
        #Updating the bitboard of the piece that is moved
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        self.bitboards[move.piece_tag] ^= mask

        #Change the bitboard of the captured piece 
        ennemy_piece_tag = "bP" if self.white_to_move else "wP"     
        index_en_passant_square = self.en_passant_square[-1][0]*8 + self.en_passant_square[-1][1]  
        self.bitboards[ennemy_piece_tag] ^= (1 << index_en_passant_square)
        self.captures.append(ennemy_piece_tag)

        #Update white, black and game bitboard
        self.update_color_and_game_bitboard()

        #Reset en passant square
        self.en_passant_square.append((0,0))

        #Leave castling info unchanged, en passant doesn't affect castling
        self.wk_can_kingside_castle.append(self.wk_can_kingside_castle[-1])
        self.bk_can_kingside_castle.append(self.bk_can_kingside_castle[-1]) 
        self.wk_can_queenside_castle.append(self.wk_can_queenside_castle[-1])
        self.bk_can_queenside_castle.append(self.bk_can_queenside_castle[-1])

        #Change turn
        self.white_to_move = not self.white_to_move    


    def make_castling_move(self, move : Move) -> None: 
        """Updates the game's attribute after castling. 

        Args:
            move (Move): The legal move to be played.
        """
        if self.white_to_move:
            self.wk_can_kingside_castle.append(False)
            self.wk_can_queenside_castle.append(False)
            self.bk_can_kingside_castle.append(self.bk_can_kingside_castle[-1])
            self.bk_can_queenside_castle.append(self.bk_can_queenside_castle[-1])
            if move.final_square[1] == 2: #Queenside
                rook_mask = 1 + (1<<3)
                self.bitboards["wR"] ^= rook_mask
                self.bitboards["wK"] = 1<<2
            else: #Kingside
                rook_mask = (1<<7) + (1<<5)
                self.bitboards["wR"] ^= rook_mask
                self.bitboards["wK"] = 1<<6
        else:
            self.bk_can_kingside_castle.append(False)
            self.bk_can_queenside_castle.append(False)
            self.wk_can_kingside_castle.append(self.wk_can_kingside_castle[-1])
            self.wk_can_queenside_castle.append(self.wk_can_queenside_castle[-1])
            if move.final_square[1] == 2: #Queenside
                rook_mask = (1<<56) + (1<<59)
                self.bitboards["bR"] ^= rook_mask
                self.bitboards["bK"] = 1<<58
            else:
                rook_mask = (1<<63) + (1<<61)
                self.bitboards["bR"] ^= rook_mask   
                self.bitboards["bK"] = 1<<62

        self.update_color_and_game_bitboard()

        self.en_passant_square.append((0,0))

        self.captures.append(None)

        self.white_to_move = not self.white_to_move      

    #TODO Promotion
    def make_move(self, move : Move) -> None:
        """Makes a move.

        Args:
            move (Move): A move to play.
        """
        self.moves.append(move)
        if move.is_en_passant_move:
            self.make_en_passant_move(move)
        elif move.is_castling_move:
            self.make_castling_move(move)
        else:
            self.make_regular_move(move)


    def make_legal_move(self, init_square : tuple[int, int], final_square : tuple[int, int], legal_moves : list[Move]) -> bool:
        """Makes a legal move on the board.

        Args:
            init_square (tuple[int, int]): The first square clicked by the user (what to move).
            final_square (tuple[int, int]): The second square clicked by the user (where to move it).
            legal_moves (list[Move]): A list of all legal moves.

        Returns:
            bool: If the move by the user was legal. Therefore, if the move was made.
        """
        for move in legal_moves:
            if init_square == move.init_square and final_square == move.final_square:
                self.make_move(move)
                return True
        return False
    

    def undo_regular_move(self, move : Move, capture : str|None) -> None:
        """Undoes a regular move.

        Args:
            move (Move): The move to be undone.
            capture (str | None): The piece tag of the captured piece if any.
        """
        #Put the moved piece back where it was
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        self.bitboards[move.piece_tag] ^= mask

        #Put back a captured piece if thje move was a capture
        if capture is not None:
            self.bitboards[capture] ^= 1 << final_index

        self.update_color_and_game_bitboard()


    def undo_castling_move(self, move : Move) -> None:
        """Undoes a castling move.

        Args:
            move (Move): The move to be undone.
        """
        #Put the king and the correct rook back
        if self.white_to_move:
            self.bitboards["bK"] = 16 << 56
            #Kingside
            if move.final_square == (7,6):
                self.bitboards["bR"] ^= (1 << 61) + (1 << 63)
            #Queenside
            if move.final_square == (7,2):
                self.bitboards["bR"] ^= (1 << 59) + (1 << 56)
        else:
            self.bitboards["wK"] = 16
            #Kingside
            if move.final_square == (0,6):
                self.bitboards["wR"] ^= (1 << 5) + (1 << 7)
            #Queenside
            if move.final_square == (0,2):
                self.bitboards["wR"] ^= (1 << 3) + 1

        self.update_color_and_game_bitboard()


    def undo_en_passant_move(self, move : Move) -> None:
        """Undoes an en passant move.

        Args:
            move (Move): The move to undo.
        """
        #Put the pawn where it was
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        self.bitboards[move.piece_tag] ^= mask

        #Put the captured pawn back
        if self.white_to_move:
            self.bitboards["wP"] ^= 1 << (final_index + 8)
        else:
            self.bitboards["bP"] ^= 1 << (final_index - 8)

        self.update_color_and_game_bitboard()

    #TODO Promotion
    def undo_move(self) -> None:
        """Undoes the last move.
        """
        #Retrieve last move and last capture
        last_move = self.moves.pop()
        last_capture = self.captures.pop()

        #Put the pieces back
        if last_move.is_en_passant_move:
            self.undo_en_passant_move(last_move)
        elif last_move.is_castling_move:
            self.undo_castling_move(last_move)
        else:
            self.undo_regular_move(last_move, last_capture)

        #Delete old data
        self.en_passant_square.pop()
        self.wk_can_kingside_castle.pop()
        self.wk_can_queenside_castle.pop()
        self.bk_can_kingside_castle.pop()
        self.bk_can_queenside_castle.pop()

        #Change turn
        self.white_to_move = not self.white_to_move