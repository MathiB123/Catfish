from move import Move

#Bottom left corner = 0
#Bottom right corner = 7
#Top right corner = 55
#Top left corner = 63

class Game:
    def __init__(self):
        #White pieces : [bitboard, tag]
        self.bitboard_white_pawns = [65280, "wP"]
        self.bitboard_white_knights = [66, "wN"]
        self.bitboard_white_bishops = [36, "wB"]
        self.bitboard_white_rooks = [129, "wR"]
        self.bitboard_white_queens = [8, "wQ"]
        self.bitboard_white_king = [16, "wK"]
        self.list_white_bitboards = [self.bitboard_white_pawns, self.bitboard_white_knights, self.bitboard_white_bishops, self.bitboard_white_rooks, self.bitboard_white_queens, self.bitboard_white_king]

        #Black pieces : [bitboard, tag]
        self.bitboard_black_pawns = [65280 << 40, "bP"]
        self.bitboard_black_knights = [66 << 56, "bN"]
        self.bitboard_black_bishops = [36 << 56, "bB"]
        self.bitboard_black_rooks = [129 << 56, "bR"]
        self.bitboard_black_queens = [8 << 56, "bQ"]
        self.bitboard_black_king = [16 << 56, "bK"]
        self.list_black_bitboards = [self.bitboard_black_pawns, self.bitboard_black_knights, self.bitboard_black_bishops, self.bitboard_black_rooks, self.bitboard_black_queens, self.bitboard_black_king]

        #Whose turn it is
        self.white_to_move = True

        #Conditions for en passant
        self.en_passant_possible = False
        self.en_passant_possible_list = [False]
        self.en_passant_square = (0,0)
        self.en_passant_square_list = [(0,0)]

        #Conditions for castling
        self.wk_can_kingside_castle = True
        self.wk_can_kingside_castle_list = [True]
        self.bk_can_kingside_castle = True
        self.bk_can_kingside_castle_list = [True]
        self.wk_can_queenside_castle = True
        self.wk_can_queenside_castle_list = [True]
        self.bk_can_queenside_castle = True
        self.bk_can_queenside_castle_list = [True]

        self.moves = []
        self.captures = []


    @staticmethod
    def get_colour_bitboard(list_colour_bitboards : list) -> int:
        """Calculates the bitboard associated with all the pieces of a certain colour.

        Args:
            list_colour_bitboards (list): The list of all bitboards of a certain colour.

        Returns:
            int: The bitboard corresponding to all the pieces of a certain colour.
        """
        colour_bitboard = 0
        for bitboard in list_colour_bitboards:
            colour_bitboard += bitboard[0]
        return colour_bitboard


    @staticmethod
    def get_game_bitboard(list_white_bitboards : list, list_black_bitboards : list) -> int:
        """Calculates the bitboard of the current position (all pieces).

        Args:
            list_white_bitboards (list): All white bitboards.
            list_black_bitboards (list): ALl black bitboards.

        Returns:
            int: The bitboard for the current position.
        """
        white_bitboard = Game.get_colour_bitboard(list_white_bitboards)
        black_bitboard = Game.get_colour_bitboard(list_black_bitboards)
        return white_bitboard + black_bitboard


    @staticmethod
    def find_indices_of_set_bits(bitboard : int) -> list:
        """Finds indices where the bits in a bitboard are set to one (the placement of a piece type).

        Args:
            bitboard (int): The bitboard corresponding to the placement of a piece type.

        Returns:
            list: The indices (squares) where the indices are placed.
        """
        indices_of_set_bits = []
        for index in range(bitboard[0].bit_length()):
            if (bitboard[0] >> index) & 1:
                i,j = divmod(int(index), 8)
                indices_of_set_bits.append((index, i, j))
        return indices_of_set_bits
    

    def get_white_pawn_moves_and_attacks(self) -> tuple[list,list]:
        """Finds pawns' moves and attacks for the white pieces.

        Returns:
            tuple[list,list]: moves, attacks.
        """
        white_pawn_moves = []
        white_pawn_attacks = []

        pieces = Game.find_indices_of_set_bits(self.bitboard_white_pawns)
        bitboard_game = Game.get_game_bitboard(self.list_white_bitboards, self.list_black_bitboards)
        bitboard_color = Game.get_colour_bitboard(self.list_black_bitboards)

        for piece in pieces:
            index, i, j = piece
            #First square in front is empty?
            if (1 << (index + 8)) & (~bitboard_game):
                white_pawn_moves.append(Move((i, j), (i+1, j), self.bitboard_white_pawns, is_promotion= i+1==7))
                #Pawn hasnt moved and the 2nd square in front is empty?
                if i == 1 and (1 << (index + 16)) & (~bitboard_game): 
                    white_pawn_moves.append(Move((i, j), (i+2, j), self.bitboard_white_pawns, en_passant_possible=True, en_passant_square=(i+2,j)))
            #Capture to the right
            if j < 7 and (1 << (index + 9)) & bitboard_color:
                white_pawn_attacks.append((i+1,j+1))
                white_pawn_moves.append(Move((i,j),(i+1,j+1), self.bitboard_white_pawns, is_promotion= i+1==7))  
            #Capture to the left
            if j > 0 and (1 << (index + 7)) & bitboard_color:
                white_pawn_attacks.append((i+1,j-1))
                white_pawn_moves.append(Move((i,j), (i+1,j-1), self.bitboard_white_pawns, is_promotion= i+1==7))
            #Capture en passant
            if i == 4 and self.en_passant_possible and (self.en_passant_square == (i,j-1) or self.en_passant_square == (i,j+1)):
                white_pawn_moves.append(Move((i,j),(self.en_passant_square[0]+1, self.en_passant_square[1]), self.bitboard_white_pawns, is_en_passant_move=True))

        return white_pawn_moves, white_pawn_attacks


    def get_black_pawn_moves_and_attacks(self) -> tuple[list,list]:
        """Finds pawns' moves and attacks for the black pieces.

        Returns:
            tuple[list,list]: moves, attacks.
        """
        black_pawn_moves = []
        black_pawn_attacks = []

        pieces = Game.find_indices_of_set_bits(self.bitboard_black_pawns)
        bitboard_game = Game.get_game_bitboard(self.list_white_bitboards, self.list_black_bitboards)
        bitboard_color = Game.get_colour_bitboard(self.list_white_bitboards)

        for piece in pieces:
            index, i, j = piece
            #First square in front is empty?
            if (1 << (index - 8)) & (~bitboard_game): 
                black_pawn_moves.append(Move((i, j), (i-1, j), self.bitboard_black_pawns, is_promotion= i-1==0))
                #Pawm hasnt moved and the 2nd square in front is empty
                if i == 6 and (1 << (index - 16)) & (~bitboard_game):
                    black_pawn_moves.append(Move((i, j), (i-2, j), self.bitboard_black_pawns, en_passant_possible=True, en_passant_square=(i-2,j)))
            #Capture to the right
            if j < 7 and (1 << (index - 7)) & bitboard_color:
                black_pawn_attacks.append((i-1,j+1))
                black_pawn_moves.append(Move((i,j),(i-1,j+1), self.bitboard_black_pawns, is_promotion= i-1==0))  
            #Capture to the left
            if j > 0 and (1 << (index - 9)) & bitboard_color:
                black_pawn_attacks.append((i-1,j-1))
                black_pawn_moves.append(Move((i,j), (i-1,j-1), self.bitboard_black_pawns, is_promotion= i-1==0))
            #Capture en passant
            if i == 3 and self.en_passant_possible and (self.en_passant_square == (i,j-1) or self.en_passant_square == (i,j+1)):
                black_pawn_moves.append(Move((i,j),(self.en_passant_square[0]-1, self.en_passant_square[1]), self.bitboard_black_pawns,is_en_passant_move=True))
            
        return black_pawn_moves, black_pawn_attacks


    def get_pawn_moves_and_attacks(self) -> tuple[list,list]:
        """Gets pawns' moves for the colour of the current turn.

        Returns:
            tuple[list,list]: Pawns' moves and attacks.
        """
        return self.get_white_pawn_moves_and_attacks() if self.white_to_move else self.get_black_pawn_moves_and_attacks()
    

    def get_knight_moves_and_attacks(self) -> tuple[list,list]:
        """Finds knights' moves and attacks.

        Returns:
            tuple[list,list]: moves and attacks.
        """
        knight_moves = []
        knight_attacks = []
        directions = ((-2,-1), (-2,1), (-1, -2), (-1, 2), (1,-2),(1,2), (2,-1), (2,1))
        bitboard_knights = self.bitboard_white_knights if self.white_to_move else self.bitboard_black_knights
        pieces = Game.find_indices_of_set_bits(bitboard_knights)
        bitboard_colour = Game.get_colour_bitboard(self.list_white_bitboards) if self.white_to_move else Game.get_colour_bitboard(self.list_black_bitboards)

        for piece in pieces:
            _, i, j = piece
            for direction in directions:
                ni, nj = i + direction[0], j + direction[1]
                #Out of bounds?
                if 0 <= ni <= 7 and 0 <= nj <= 7:
                    #Enemy piece?
                    if (1 << (8*ni + nj)) & (~bitboard_colour):
                        knight_attacks.append((ni,nj))
                        knight_moves.append(Move((i,j),(ni,nj), bitboard_knights))
                         
        return knight_moves, knight_attacks
    

    def get_bishop_moves_and_attacks(self, is_queen_move = False) -> tuple[list,list]:
        """Finds bishops' moves and attacks.

        Args:
            is_queen_move (bool, optional): Are we calculating the moves for the queen. Defaults to False.

        Returns:
            tuple[list,list]: moves and attacks.
        """
        bishop_moves = []
        bishop_attacks = []
        directions = ((-1,-1), (-1,1), (1,-1), (1,1))

        if self.white_to_move:
            bitboard_bishops = self.bitboard_white_queens if is_queen_move else self.bitboard_white_bishops
            bitboard_colour = Game.get_colour_bitboard(self.list_black_bitboards)
        else:
            bitboard_bishops = self.bitboard_black_queens if is_queen_move else self.bitboard_black_bishops
            bitboard_colour = Game.get_colour_bitboard(self.list_white_bitboards)

        pieces = Game.find_indices_of_set_bits(bitboard_bishops)

        for piece in pieces:
            _, i, j = piece
            for direction in directions:
                k=1
                while 0 <= i + k*direction[0] <= 7 and 0 <= j + k*direction[1] <= 7:
                    if (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & (~Game.get_game_bitboard(self.list_white_bitboards, self.list_black_bitboards)):
                        bishop_moves.append(Move((i,j),(i+k*direction[0],j+k*direction[1]),bitboard_bishops))
                        bishop_attacks.append((i+k*direction[0],j+k*direction[1]))                      
                    elif (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & bitboard_colour:
                        bishop_moves.append(Move((i,j),(i+k*direction[0],j+k*direction[1]),bitboard_bishops))
                        bishop_attacks.append((i+k*direction[0],j+k*direction[1]))
                        break
                    else:
                        break
                    k+=1

        return bishop_moves, bishop_attacks                       
    

    def get_rook_moves_and_attacks(self, is_queen_move=False) -> tuple[list,list]:
        """Finds rooks' moves and attacks.

        Args:
            is_queen_move (bool, optional): Are we calculating the moves for the queen. Defaults to False.

        Returns:
            tuple[list,list]: moves and attacks.
        """
        rook_moves = []
        rook_attacks = []
        directions = ((-1,0), (0,-1), (1,0), (0,1))

        if self.white_to_move:
            bitboard_rooks = self.bitboard_white_queens if is_queen_move else self.bitboard_white_rooks
            bitboard_colour = Game.get_colour_bitboard(self.list_black_bitboards)
        else:
            bitboard_rooks = self.bitboard_black_queens if is_queen_move else self.bitboard_black_rooks
            bitboard_colour = Game.get_colour_bitboard(self.list_white_bitboards)

        pieces = Game.find_indices_of_set_bits(bitboard_rooks)

        for piece in pieces:
            _, i, j = piece
            for direction in directions:
                k=1 
                while 0 <= i + k*direction[0] <= 7 and 0 <= j + k*direction[1] <= 7:
                    if (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & (~Game.get_game_bitboard(self.list_white_bitboards, self.list_black_bitboards)):
                        rook_moves.append(Move((i,j),(i+k*direction[0],j+k*direction[1]),bitboard_rooks))
                        rook_attacks.append((i+k*direction[0],j+k*direction[1]))
                    elif (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & bitboard_colour:
                        rook_moves.append(Move((i,j),(i+k*direction[0],j+k*direction[1]),bitboard_rooks))
                        rook_attacks.append((i+k*direction[0],j+k*direction[1]))
                        break
                    else:
                        break
                    k+=1

        return rook_moves, rook_attacks
    

    def get_queen_moves_and_attacks(self) -> tuple[list,list]:
        """Finds queens' moves and attacks.

        Returns:
            tuple[list,list]: moves and attacks.
        """
        queen_moves = []
        queen_attacks = []
        bitboard_queens = self.bitboard_white_queens if self.white_to_move else self.bitboard_black_queens

        pieces = Game.find_indices_of_set_bits(bitboard_queens)

        for _ in pieces:
            a,c = self.get_bishop_moves_and_attacks(is_queen_move=True)
            b,d = self.get_rook_moves_and_attacks(is_queen_move=True)
            queen_moves.extend(a)
            queen_moves.extend(b)
            queen_attacks.extend(c)
            queen_attacks.extend(d)
        
        return queen_moves, queen_attacks 
    
    
    @staticmethod
    def all_around_king(index : int) -> int:
        """Bitboard for the squares around the king.

        Args:
            index (int): king position.

        Returns:
            int: Bitboard for the squares around the king.
        """
        all_around_k = 0
        i,j = divmod(index, 8)
        directions = ((-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1))
        for direction in directions:
            if 0 <= i + direction[0] <= 7 and 0 <= j + direction[1] <= 7:
                all_around_k += (1 << ((i+direction[0])*8 + (j+direction[1])))
        return all_around_k


    def get_king_moves_and_attacks(self) -> tuple[list,list]:
        """Finds king moves and attacks.

        Returns:
            tuple[list,list]: moves, attacks.
        """
        king_moves, king_attacks = [], []

        bitboard_king = self.bitboard_white_king if self.white_to_move else self.bitboard_black_king
        bitboard_opp_king = self.bitboard_black_king if self.white_to_move else self.bitboard_white_king
        bitboard_colour = Game.get_colour_bitboard(self.list_white_bitboards) if self.white_to_move else Game.get_colour_bitboard(self.list_black_bitboards)
        original_king_square = (0,4) if self.white_to_move else (7,4)

        _, i, j = Game.find_indices_of_set_bits(bitboard_king)[0]
        index, __, ___ = Game.find_indices_of_set_bits(bitboard_opp_king)[0]
        directions = ((-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1))

        #Normal king moves
        for direction in directions:
            if 0 <= i + direction[0] <= 7 and 0 <= j + direction[1] <= 7:
                if (1 << ((i+direction[0])*8 + (j+direction[1]))) & ~bitboard_colour and not ((1 << ((i+direction[0])*8 + (j+direction[1]))) & Game.all_around_king(index)):
                    king_moves.append(Move((i,j),(i+direction[0],j+direction[1]),bitboard_king))
                    king_attacks.append((i+direction[0],j+direction[1]))    

        #Castling
        if (i,j) == (original_king_square):
            if self.white_to_move:
                if self.wk_can_kingside_castle:
                    kingside_castling = self.get_kingside_castle_white()
                    king_moves.extend(kingside_castling)
                if self.wk_can_queenside_castle:
                    queenside_castling = self.get_queenside_castle_white()
                    king_moves.extend(queenside_castling)
            else:
                if self.bk_can_kingside_castle:
                    kingside_castling = self.get_kingside_castle_black()
                    king_moves.extend(kingside_castling)
                if self.bk_can_queenside_castle:
                    queenside_castling = self.get_queenside_castle_black()
                    king_moves.extend(queenside_castling)     

        return king_moves, king_attacks


    def get_kingside_castle_white(self) -> list:
        """Can the white king kinside castle.

        Returns:
            list: The castling move if castling is available.
        """
        color_bitboard = Game.get_colour_bitboard(self.list_white_bitboards)
        if (1<<5) & ~color_bitboard:
            if (1<<6) & ~color_bitboard:
                temp_kingside = True if self.bk_can_kingside_castle else False
                temp_queenside = True if self.bk_can_queenside_castle else False
                self.bk_can_kingside_castle = False
                self.bk_can_queenside_castle = False
                self.white_to_move = False
                attacks = self.get_all_possible_moves_and_attacks()[1]
                self.bk_can_kingside_castle = temp_kingside
                self.bk_can_queenside_castle = temp_queenside
                self.white_to_move = True
                for attack in attacks:
                    if attack == (0,5) or attack == (0,6):
                        return []
                return [Move((0,4),(0,6),self.bitboard_white_king, is_castling_move=True)]
        return []
    

    def get_queenside_castle_white(self) -> list:
        """Can the white king queenside castle.

        Returns:
            list: The castling move if available.
        """
        color_bitboard = Game.get_colour_bitboard(self.list_white_bitboards)
        if (1<<3) & ~color_bitboard:
            if (1<<2) & ~color_bitboard:
                if (1<<1) & ~color_bitboard:
                    temp_kingside = True if self.bk_can_kingside_castle else False
                    temp_queenside = True if self.bk_can_queenside_castle else False
                    self.bk_can_kingside_castle = False
                    self.bk_can_queenside_castle = False
                    self.white_to_move = False
                    attacks = self.get_all_possible_moves_and_attacks()[1]
                    self.bk_can_kingside_castle = temp_kingside
                    self.bk_can_queenside_castle = temp_queenside
                    self.white_to_move = True
                    for attack in attacks:
                        if attack == (0,2) or attack == (0,3):
                            return []
                    return [Move((0,4),(0,2), self.bitboard_white_king, is_castling_move=True)]
        return []        


    def get_kingside_castle_black(self) -> list:
        """Can the black king kingside castle.

        Returns:
            list: The castling move if available.
        """
        color_bitboard  = Game.get_colour_bitboard(self.list_black_bitboards)
        if (1<<61) & ~color_bitboard:
            if (1<<62) & ~color_bitboard:
                temp_kingside = True if self.wk_can_kingside_castle else False
                temp_queenside = True if self.wk_can_queenside_castle else False
                self.wk_can_kingside_castle = False
                self.wk_can_queenside_castle = False
                self.white_to_move = True
                attacks = self.get_all_possible_moves_and_attacks()[1]
                self.wk_can_kingside_castle = temp_kingside
                self.wk_can_queenside_castle = temp_queenside
                self.white_to_move = False
                for attack in attacks:
                    if attack == (7,5) or attack == (7,6):
                        return []
                return [Move((7,4),(7,6),self.bitboard_black_king, is_castling_move=True)]
        return []            


    def get_queenside_castle_black(self) -> list:
        """Can the black king queenside castle.

        Returns:
            list: The castling move if available.
        """
        color_bitboard = Game.get_colour_bitboard(self.list_black_bitboards)
        if (1<<57) & ~color_bitboard:
            if (1<<58) & ~color_bitboard:
                if (1<<59) & ~color_bitboard:
                    temp_kingside = True if self.wk_can_kingside_castle else False
                    temp_queenside = True if self.wk_can_queenside_castle else False
                    self.wk_can_kingside_castle = False
                    self.wk_can_queenside_castle = False
                    self.white_to_move = True
                    attacks = self.get_all_possible_moves_and_attacks()[1]
                    self.wk_can_kingside_castle = temp_kingside
                    self.wk_can_queenside_castle = temp_queenside
                    self.white_to_move = False
                    for attack in attacks:
                        if attack == (7,2) or attack == (7,3):
                            return []
                    return [Move((7,4),(7,2), self.bitboard_black_king, is_castling_move=True)]
        return []      
    

    def get_all_possible_moves_and_attacks(self) -> tuple[list,list]:
        """Gets all moves and attacks in a given position.

        Returns:
            tuple[list,list]: moves, attacks.
        """
        all_moves = []
        all_attacks = []
        functions = [self.get_pawn_moves_and_attacks(), self.get_knight_moves_and_attacks(), self.get_bishop_moves_and_attacks(), self.get_rook_moves_and_attacks(), self.get_queen_moves_and_attacks(), self.get_king_moves_and_attacks()]
        for function in functions:
            moves, attacks = function
            all_moves.extend(moves)
            all_attacks.extend(attacks)
        return all_moves, all_attacks
    

    def get_all_legal_moves(self) -> list:
        """Finds all legal moves in a position.

        Returns:
            list: legal moves.
        """
        all_possible_moves = self.get_all_possible_moves_and_attacks()[0]
        all_legal_moves = []

        for move in all_possible_moves:
            #Move the piece
            init_index = move.init_square[0]*8 + move.init_square[1]
            final_index = move.final_square[0]*8 + move.final_square[1]
            mask = (1 << init_index) + (1 << final_index)
            move.bb_piece[0] ^= mask 

            #Capturing something
            bb_capture = None
            bitboards_colour = self.list_black_bitboards if self.white_to_move else self.list_white_bitboards
            for bitboard in bitboards_colour:
                if bitboard[0] & (1 << final_index):
                    bitboard[0] ^= (1 << final_index)
                    bb_capture = bitboard
                    break
            

            self.white_to_move = not self.white_to_move
            opp_moves = self.get_all_possible_moves_and_attacks()[0]
            self.white_to_move = not self.white_to_move
            
            bb_king = self.bitboard_white_king if self.white_to_move else self.bitboard_black_king
            indices_king = self.find_indices_of_set_bits(bb_king)[0]
            king_position = (indices_king[1],indices_king[2])

            move.bb_piece[0] ^= mask
            if bb_capture is not None:
                bb_capture[0] ^= (1<<final_index)

            to_remove = False
            for opp_move in opp_moves:
                if opp_move.final_square == king_position:
                    to_remove = True
                    break    

            if not to_remove:
                all_legal_moves.append(move)
                
        return all_legal_moves


    def move_played(self, init_square : tuple, final_square : tuple) -> tuple[bool,Move]:
        """Validates a move before playing it (is the move legal?).

        Args:
            init_square (tuple): Initial square of the piece.
            final_square (tuple): Final square of the piece.

        Returns:
            tuple[bool,Move]: The move can be made, what the move was (None if the move is not valid).
        """
        move_to_be = Move(init_square, final_square, None)
        all_moves = self.get_all_legal_moves()

        for allowed_move in all_moves:
            if move_to_be == allowed_move:
                self.wk_can_kingside_castle_list.append(self.wk_can_kingside_castle)
                self.wk_can_queenside_castle_list.append(self.wk_can_queenside_castle)
                self.bk_can_kingside_castle_list.append(self.bk_can_kingside_castle)
                self.bk_can_queenside_castle_list.append(self.bk_can_queenside_castle)
                self.en_passant_possible_list.append(self.en_passant_possible)
                self.en_passant_square_list.append(self.en_passant_square)
                self.moves.append(allowed_move)
                if allowed_move.is_en_passant_move:
                    self.make_en_passant_move(allowed_move)
                    return True, allowed_move
                elif allowed_move.is_castling_move:
                    self.make_castling_move(allowed_move)
                    return True, allowed_move
                elif allowed_move.is_promotion:
                    self.make_promotion_move(allowed_move)
                    return True, allowed_move
                else: 
                    self.make_move(allowed_move)
                    return True, allowed_move
            
        return False, None


    def make_move(self, move: Move) -> None:
        """Plays a normal move.

        Args:
            move (Move): The move to be played.
        """
        #Updating the bitboard of the piece that is moved
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        move.bb_piece[0] ^= mask     

        #Change the bitboard of a captured if the move is a capture
        bitboards_colour = self.list_black_bitboards if self.white_to_move else self.list_white_bitboards
        bb_capture = None
        for bitboard in bitboards_colour:
            if bitboard[0] & (1 << final_index):
                bitboard[0] ^= (1 << final_index)
                bb_capture = bitboard
                break
        self.captures.append(bb_capture)

        #Change en passant conditions
        self.en_passant_possible = move.en_passant_possible
        self.en_passant_square = move.en_passant_square

        #Cant castle if we move a rook
        if move.init_square == (0,0):
            self.wk_can_queenside_castle = False
        if move.init_square == (0,7):
            self.wk_can_kingside_castle = False
        if move.init_square == (7,0):
            self.bk_can_queenside_castle = False
        if move.init_square == (7,7):
            self.bk_can_kingside_castle = False

        #Cant castle if we move the king
        if move.init_square == (0,4):
            self.wk_can_kingside_castle = False
            self.wk_can_queenside_castle = False
        if move.init_square == (7,4):
            self.bk_can_kingside_castle = False
            self.bk_can_queenside_castle = False

        self.white_to_move = not self.white_to_move


    def make_en_passant_move(self, move: Move) -> None:
        """Plays an en passant move.

        Args:
            move (Move): The move to be played.
        """
        #Updating the bitboard of the piece that is moved
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        move.bb_piece[0] ^= mask     

        #Change the bitboard of the captured piece 
        bitboard_colour = self.bitboard_black_pawns if self.white_to_move else self.bitboard_white_pawns     
        index_en_passant_square = self.en_passant_square[0]*8 + self.en_passant_square[1]  
        bitboard_colour[0] ^= (1 << index_en_passant_square)
        self.captures.append(bitboard_colour)

        self.white_to_move = not self.white_to_move

        self.en_passant_possible = move.en_passant_possible
        self.en_passant_square = move.en_passant_square


    def make_castling_move(self, move : Move) -> None:
        """Plays a castling move.

        Args:
            move (Move): The move to be played.
        """
        if self.white_to_move:
            if move.final_square[1] == 2: #Queenside
                self.wk_can_queenside_castle, self.wk_can_kingside_castle = False, False
                rook_mask = 1 + (1<<3)
                self.bitboard_white_rooks[0] ^= rook_mask
                self.bitboard_white_king[0] = 1<<2
            else: #Kingside
                self.wk_can_queenside_castle, self.wk_can_kingside_castle = False, False
                rook_mask = (1<<7) + (1<<5)
                self.bitboard_white_rooks[0] ^= rook_mask
                self.bitboard_white_king[0] = 1<<6
        else:
            if move.final_square[1] == 2: #Queenside
                self.bk_can_queenside_castle, self.bk_can_kingside_castle = False, False
                rook_mask = (1<<56) + (1<<59)
                self.bitboard_black_rooks[0] ^= rook_mask
                self.bitboard_black_king[0] = 1<<58
            else: #Kingside
                self.bk_can_queenside_castle, self.bk_can_kingside_castle = False, False
                rook_mask = (1<<63) + (1<<61)
                self.bitboard_black_rooks[0] ^= rook_mask   
                self.bitboard_black_king[0] = 1<<62

        self.captures.append(None)

        self.white_to_move = not self.white_to_move      


    def make_promotion_move(self, move : Move) -> None:
        promoted_piece = None
        promotion = input("What piece to promote to?")
        match promotion:
            case "N":
                promoted_piece = self.bitboard_white_knights if self.white_to_move else self.bitboard_black_knights
            case "B":
                promoted_piece = self.bitboard_white_bishops if self.white_to_move else self.bitboard_black_bishops
            case "R":
                promoted_piece = self.bitboard_white_rooks if self.white_to_move else self.bitboard_black_rooks
            case "Q":
                promoted_piece = self.bitboard_white_queens if self.white_to_move else self.bitboard_black_queens        
        
        #Updating the bitboard of the piece that is moved
        init_index = move.init_square[0]*8 + move.init_square[1]
        move.bb_piece[0] ^= (1 << init_index)
        final_index = move.final_square[0]*8 + move.final_square[1]
        promoted_piece[0] ^= (1 << final_index)

        #Change the bitboard of a captured if the move is a capture
        bitboards_colour = self.list_black_bitboards if self.white_to_move else self.list_white_bitboards
        bb_capture = None
        for bitboard in bitboards_colour:
            if bitboard[0] & (1 << final_index):
                bitboard[0] ^= (1 << final_index)
                bb_capture = bitboard
                break
        self.captures.append(bb_capture)

        #Change en passant conditions
        self.en_passant_possible = move.en_passant_possible
        self.en_passant_square = move.en_passant_square

        self.white_to_move = not self.white_to_move


    def undo_move(self) -> None:
        """Undoes the previous move.
        """
        last_move = self.moves.pop()
        if last_move.is_en_passant_move:
            self.undo_en_passant_move(last_move)
        elif last_move.is_castling_move:
            self.undo_castle_move(last_move)
        elif last_move.is_promotion:
            self.undo_promotion_move(last_move)
        else:
            self.undo_regular_move(last_move)
        self.captures.pop()
        self.wk_can_kingside_castle_list.pop()
        self.wk_can_queenside_castle_list.pop()
        self.bk_can_kingside_castle_list.pop()
        self.bk_can_queenside_castle_list.pop()
        self.en_passant_possible_list.pop()
        self.en_passant_square_list.pop()

    def undo_promotion_move(self, move : Move):
        init_index = move.init_square[0]*8 + move.init_square[1]
        move.bb_piece[0] ^= 1 << init_index
        final_index = move.final_square[0]*8 + move.final_square[1]
        ls_bb = self.list_black_bitboards if self.white_to_move else self.list_white_bitboards
        for bb in ls_bb:
            if bb[0] & (1 << final_index):
                bb[0] ^= 1 << final_index 
                break
        
        if self.captures[-1] is not None:
            self.captures[-1][0] ^= 1 << final_index

        self.en_passant_possible = self.en_passant_possible_list[-1]
        self.en_passant_square = self.en_passant_square_list[-1]

        self.white_to_move = not self.white_to_move
        
        self.wk_can_kingside_castle = self.wk_can_kingside_castle_list[-1]
        self.wk_can_queenside_castle = self.wk_can_queenside_castle_list[-1]
        self.bk_can_kingside_castle = self.bk_can_kingside_castle_list[-1]
        self.bk_can_queenside_castle = self.bk_can_queenside_castle_list[-1]


    def undo_regular_move(self, move:Move) -> None:
        """Undoes a regular move. 

        Args:
            move (Move): The move to be undone.
        """
        init_index = move.init_square[0]*8 + move.init_square[1]
        final_index = move.final_square[0]*8 + move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        move.bb_piece[0] ^= mask

        if self.captures[-1] is not None: 
            self.captures[-1][0] ^= 1 << final_index
        
        self.en_passant_possible = self.en_passant_possible_list[-1]
        self.en_passant_square = self.en_passant_square_list[-1]

        self.white_to_move = not self.white_to_move
        
        self.wk_can_kingside_castle = self.wk_can_kingside_castle_list[-1]
        self.wk_can_queenside_castle = self.wk_can_queenside_castle_list[-1]
        self.bk_can_kingside_castle = self.bk_can_kingside_castle_list[-1]
        self.bk_can_queenside_castle = self.bk_can_queenside_castle_list[-1]


    def undo_castle_move(self, castle_move : Move) -> None:
        """Undoes a castling move.

        Args:
            castle_move (Move): Castling move to undo.
        """
        self.white_to_move = not self.white_to_move
        self.make_castling_move(castle_move)
        self.white_to_move = not self.white_to_move

        if self.white_to_move:
            self.bitboard_white_king[0] = 16
        else:
            self.bitboard_black_king[0] = 16 << 56
        
        self.wk_can_kingside_castle = self.wk_can_kingside_castle_list[-1]
        self.wk_can_queenside_castle = self.wk_can_queenside_castle_list[-1]
        self.bk_can_kingside_castle = self.bk_can_kingside_castle_list[-1]
        self.bk_can_queenside_castle = self.bk_can_queenside_castle_list[-1]

   
    def undo_en_passant_move(self, en_passant_move : Move) -> None:
        """Undoes an en passant move.

        Args:
            en_passant_move (Move): en passant move to undo.
        """
        init_index = en_passant_move.init_square[0]*8 + en_passant_move.init_square[1]
        final_index = en_passant_move.final_square[0]*8 + en_passant_move.final_square[1]
        mask = (1 << init_index) + (1 << final_index)
        en_passant_move.bb_piece[0] ^= mask

        bb_enemy = self.bitboard_white_pawns if self.white_to_move else self.bitboard_black_pawns

        if not self.white_to_move:
            bb_enemy[0] ^= 1 << (final_index - 8) 
        else:
            bb_enemy[0] ^= 1 << (final_index + 8)

        self.en_passant_possible = True

        if not self.white_to_move:
            self.en_passant_square = (en_passant_move.final_square[0]-1,en_passant_move.final_square[1])
        else:
            self.en_passant_square = (en_passant_move.final_square[0]+1,en_passant_move.final_square[1])

        self.white_to_move = not self.white_to_move

        self.wk_can_kingside_castle = self.wk_can_kingside_castle_list[-1]
        self.wk_can_queenside_castle = self.wk_can_queenside_castle_list[-1]
        self.bk_can_kingside_castle = self.bk_can_kingside_castle_list[-1]
        self.bk_can_queenside_castle = self.bk_can_queenside_castle_list[-1]