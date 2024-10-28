### This file implements the move generation algorithm. ###

from game_logic.move import Move
from game_logic.game_state import Game

def find_coordinates(bitboard : int) -> tuple[int, int, int]:
    """Finds the square location and position (i,j) on the board of a piece type. 

    Args:
        bitboard (int): The bitboard associated with the piece type.

    Returns:
        tuple[int, int, int]: The square, the i coordinate and the j coordinate.
    """
    coordinates = []
    current_square = 0

    while bitboard > 0: #Checking each bit to find if the value is 1
        if bitboard & 1 == 1:
            i,j = divmod(int(current_square), 8)
            coordinates.append((current_square, i, j))
        bitboard >>= 1
        current_square += 1

    return coordinates


def get_white_pawn_moves(bitboards : dict, en_passant_square : tuple[int, int]) -> list[Move]:
    """Finds the moves of the white pawns.

    Args:
        bitboards (dict): The bitboards for the current position.
        en_passant_square (tuple[int, int]): Current en passant square. (0,0) if none else (x,y).

    Returns:
        list[Move]: The moves of the white pawns.
    """
    white_pawn_moves = []
    wP_bitboard = bitboards["wP"]

    coordinates = find_coordinates(wP_bitboard)
    for coordinate in coordinates:
        square, i, j = coordinate
        #First square in front is empty?
        if (1 << (square + 8)) & ~bitboards["game"]:
            white_pawn_moves.append(Move((i,j), (i+1,j), "wP", is_promotion = i+1==7))
            #Second square in front empty and pawn hasn't moved before?
            if i==1 and ((1 << (square + 16)) & ~bitboards["game"]):
                white_pawn_moves.append(Move((i,j), (i+2,j), "wP", en_passant_square = (i+2,j)))
        #Capture to the right
        if j < 7 and ((1 << (square + 9)) & bitboards["black"]):
            white_pawn_moves.append(Move((i,j), (i+1,j+1), "wP", is_promotion = i+1==7))
        #Capture to the left
        if j > 0 and ((1 << (square + 7)) & bitboards["black"]):
            white_pawn_moves.append(Move((i,j), (i+1,j-1), "wP", is_promotion = i+1==7))
        #En passant
        if i==4 and (en_passant_square == (i, j-1) or en_passant_square == (i, j+1)):
            white_pawn_moves.append(Move((i,j), (en_passant_square[0] + 1, en_passant_square[1]), "wP", is_en_passant_move=True))

    return white_pawn_moves


def get_black_pawn_moves(bitboards : dict, en_passant_square : tuple[int, int]) -> list[Move]:
    """Finds the moves of the black pawns.

    Args:
        bitboards (dict): The bitboards for the current position.
        en_passant_square (tuple[int, int]): Current en passant square. (0,0) if none else (x,y).

    Returns:
        list[Move]: The moves of the black pawns.
    """    
    black_pawn_moves = []
    bP_bitboard = bitboards["bP"]   

    coordinates = find_coordinates(bP_bitboard)
    for coordinate in coordinates:
        square, i,j = coordinate
        #First square in front is empty?
        if (1 << (square - 8)) & ~bitboards["game"]:
            black_pawn_moves.append(Move((i,j), (i-1,j), "bP", is_promotion = i-1==0))
            #Second square in front is empty?
            if i == 6 and ((1 << (square - 16)) & ~bitboards["game"]):
                black_pawn_moves.append(Move((i,j), (i-2,j), "bP", en_passant_square = (i-2,j)))
        #Capture to the right (from white's perspective)
        if j < 7 and ((1 << (square - 7)) & bitboards["white"]):
            black_pawn_moves.append(Move((i,j), (i-1,j+1), "bP", is_promotion = i-1==0))
        #Capture to the left (from white's perspective)
        if j > 0 and ((1 << (square - 9)) & bitboards["white"]):
            black_pawn_moves.append(Move((i,j), (i-1,j-1), "bP", is_promotion = i-1==0)) 
        #En passant 
        if i==3 and (en_passant_square == (i, j-1) or en_passant_square == (i,j+1)):
            black_pawn_moves.append(Move((i,j), (en_passant_square[0]-1, en_passant_square[1]), "bP", is_en_passant_move=True))
            
    return black_pawn_moves


def get_pawn_moves(bitboards : dict, en_passant_square : tuple[int, int], white_to_move : bool) -> list[Move]:
    """Finds the moves of the pawns for the current turn.

    Args:
        bitboards (dict): The bitboards for the current position.
        en_passant_square (tuple[int, int]): Current en passant square. (0,0) if none else (x,y).
        white_to_move (bool): Is it white to move?

    Returns:
        list[Move]: The moves of the pawns for the current turn.
    """
    return get_white_pawn_moves(bitboards, en_passant_square) if white_to_move else get_black_pawn_moves(bitboards, en_passant_square)


def get_knight_moves(bitboards : dict, white_to_move : bool) -> list[Move]:
    """Finds the moves of the knights.

    Args:
        bitboards (dict): The bitboards for the current position.
        white_to_move (bool): Is it white to move?

    Returns:
        list[Move]: The moves of the knights for the current position.
    """
    knight_moves = []
    directions = ((-2,-1), (-2,1), (-1, -2), (-1, 2), (1,-2),(1,2), (2,-1), (2,1))

    if white_to_move:
        N_bitboard, ally_pieces, piece_tag = bitboards["wN"], bitboards["white"], "wN"
    else:
        N_bitboard, ally_pieces, piece_tag = bitboards["bN"], bitboards["black"], "bN"

    coordinates = find_coordinates(N_bitboard)
    for coordinate in coordinates:
        _, i, j = coordinate
        for direction in directions:
            ni, nj = i + direction[0], j + direction[1]
            #Out of bounds?
            if 0 <= ni <= 7 and 0 <= nj <= 7:
                if (1 << (8*ni + nj)) & ~ally_pieces:
                    knight_moves.append(Move((i,j), (ni,nj), piece_tag))
                         
    return knight_moves


def get_bishop_moves(bitboards : dict, white_to_move : bool, is_queen_move : bool) -> list[Move]:
    """Finds the moves of the bishops.

    Args:
        bitboards (dict): The bitboards for the current position.
        white_to_move (bool): Is it white to move?
        is_queen_move (bool): Is the function used to calculate the moves for the queen?

    Returns:
        list[Move]: The moves for the bishops in the current position.
    """
    bishop_moves = []
    directions = ((-1,-1), (-1,1), (1,-1), (1,1))

    if white_to_move:
        enemy_pieces = bitboards["black"]
        if is_queen_move:
            B_bitboard, piece_tag = bitboards["wQ"], "wQ" 
        else:
            B_bitboard, piece_tag = bitboards["wB"], "wB"
    else:
        enemy_pieces = bitboards["white"]
        if is_queen_move:
            B_bitboard, piece_tag = bitboards["bQ"], "bQ" 
        else:
            B_bitboard, piece_tag = bitboards["bB"], "bB"

    coordinates = find_coordinates(B_bitboard)
    for coordinate in coordinates:
        _, i, j = coordinate
        for direction in directions:
            k=1
            while 0 <= i + k*direction[0] <= 7 and 0 <= j + k*direction[1] <= 7:
                #Empty square
                if (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & ~bitboards["game"]:
                    bishop_moves.append(Move((i,j), (i+k*direction[0],j+k*direction[1]), piece_tag))
                #Square with enemy piece
                elif (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & enemy_pieces:
                    bishop_moves.append(Move((i,j), (i+k*direction[0],j+k*direction[1]), piece_tag))
                    break
                #Square with ally piece
                else:
                    break
                k += 1
    
    return bishop_moves
                      

def get_rook_moves(bitboards : dict, white_to_move : bool, is_queen_move : bool) -> list[Move]:
    """Finds the moves of the rooks.

    Args:
        bitboards (dict): The bitboards for the current position.
        white_to_move (bool): Is it white to move?
        is_queen_move (bool): Is the function used to calculate the moves for the queen?

    Returns:
        list[Move]: The moves of the rooks in the current position.
    """
    rook_moves = []
    directions = ((-1,0), (0,-1), (1,0), (0,1))

    if white_to_move:
        enemy_pieces = bitboards["black"]
        if is_queen_move:
            R_bitboard, piece_tag = bitboards["wQ"], "wQ"
        else:    
            R_bitboard, piece_tag = bitboards["wR"], "wR"
    else:
        enemy_pieces = bitboards["white"]
        if is_queen_move:
            R_bitboard, piece_tag = bitboards["bQ"], "bQ" 
        else:
            R_bitboard, piece_tag = bitboards["bR"], "bR"

    coordinates = find_coordinates(R_bitboard)
    for coordinate in coordinates:
        _, i, j = coordinate
        for direction in directions:
            k=1
            while 0 <= i + k*direction[0] <= 7 and 0 <= j + k*direction[1] <= 7:
                if (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & ~bitboards["game"]:
                    rook_moves.append(Move((i,j), (i+k*direction[0], j+k*direction[1]), piece_tag))
                elif (1 << ((i+k*direction[0])*8 + (j+k*direction[1]))) & enemy_pieces:
                    rook_moves.append(Move((i,j), (i+k*direction[0], j+k*direction[1]), piece_tag))
                    break
                else:
                    break
                k+=1

    return rook_moves


def get_queen_moves(bitboards : dict, white_to_move : bool) -> list[Move]:
    """Finds the moves of the queen.

    Args:
        bitboards (dict): The bitboards for the current position.
        white_to_move (bool): Is it white to move?

    Returns:
        list[Move]: The moves of the queen in the current position.
    """
    queen_moves = []

    bishop_like_moves= get_bishop_moves(bitboards, white_to_move, True)
    rook_like_moves = get_rook_moves(bitboards, white_to_move, True)

    queen_moves.extend(bishop_like_moves)
    queen_moves.extend(rook_like_moves)

    return queen_moves 


def get_king_moves(bitboards : dict, white_to_move : bool, castling : dict) -> list[Move]:
    """Finds the moves of the king including castling if available.

    Args:
        bitboards (dict): The bitboards for the current position.
        white_to_move (bool): Is it white to move?
        castling (dict): Castling info from the current position.

    Returns:
        list[Move]: The moves of the king in the current position.
    """
    king_moves = []
    directions = ((-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1))

    if white_to_move:
        K_bitboard, ally_pieces, piece_tag, original_square = bitboards["wK"], bitboards["white"], "wK", (0,4)
    else:
        K_bitboard, ally_pieces, piece_tag, original_square = bitboards["bK"], bitboards["black"], "bK", (7,4)

    coordinates = find_coordinates(K_bitboard)[0]
    _, i, j = coordinates
    #Normal king moves
    for direction in directions:
        if 0 <= i + direction[0] <= 7 and 0 <= j + direction[1] <= 7:
            if ((1 << ((i+direction[0])*8 + (j+direction[1]))) & ~ally_pieces):
                king_moves.append(Move((i,j), (i+direction[0],j+direction[1]), piece_tag))

    #Castling
    if (i,j) == original_square:
        if white_to_move:
            if castling["wkk"]:
                king_moves.extend(get_white_kingside_castle(bitboards["white"]))
            if castling["wkq"]:
                king_moves.extend(get_white_queenside_castle(bitboards["white"]))
        else:
            if castling["bkk"]:
                king_moves.extend(get_black_kingside_castle(bitboards["black"]))
            if castling["bkq"]:
                king_moves.extend(get_black_queenside_castle(bitboards["black"]))

    return king_moves


def get_white_kingside_castle(white_bitboard : dict) -> list[Move]:
    """Checks if white can castle kingside.

    Args:
        white_bitboard (dict): Bitboard for the white pieces.

    Returns:
        list[Move]: Kingside castle move.
    """
    if ((1 << 5) & ~white_bitboard) and  ((1 << 6) & ~white_bitboard):
        return [Move((0,4), (0,6), "wK", is_castling_move=True)]
    return []


def get_black_kingside_castle(black_bitboard : dict) -> list[Move]:
    """Checks if black can castle kingside.

    Args:
        black_bitboard (dict): Bitboard for the black pieces.

    Returns:
        list[Move]: Kingside castle move.
    """
    if ((1 << 61) & ~black_bitboard) and ((1 << 62) & ~black_bitboard):
        return [Move((7,4), (7,6), "bK", is_castling_move=True)]
    return []


def get_white_queenside_castle(white_bitboard : dict) -> list[Move]:
    """Checks if white can castle queenside.

    Args:
        white_bitboard (dict): Bitboard for the white pieces.

    Returns:
        list[Move]: Queenside castle move.
    """
    if ((1 << 1) & ~white_bitboard) and ((1 << 2) & ~white_bitboard) and ((1 << 3) & ~white_bitboard):
        return [Move((0,4), (0,2), "wK", is_castling_move=True)]
    return []


def get_black_queenside_castle(black_bitboard : dict) -> list[Move]:
    """Checks if black can castle queenside.

    Args:
        black_bitboard (dict): Bitboard for the black pieces.

    Returns:
        list[Move]: Queenside castle move.
    """
    if ((1 << 57) & ~black_bitboard) and ((1 << 58) & ~black_bitboard) and ((1 << 59) & ~black_bitboard):
        return [Move((7,4), (7,2), "bK", is_castling_move=True)]
    return []


def get_all_possible_moves(bitboards : dict, en_passant_square : tuple[int, int], white_to_move : bool, castling : dict) -> list[Move]:
    """Finds all possible moves (not necessarily legal) in the position.

    Args:
        bitboards (dict): The bitboards for the current position.
        en_passant_square (tuple[int, int]): Current en passant square. (0,0) if none else (x,y).
        white_to_move (bool): Whose turn it is.
        castling (dict): Castling info from the current position.

    Returns:
        list[Move]: The possible moves.
    """
    pawn_moves = get_pawn_moves(bitboards, en_passant_square, white_to_move)
    knight_moves = get_knight_moves(bitboards, white_to_move)
    bishop_moves = get_bishop_moves(bitboards, white_to_move, False)
    rook_moves = get_rook_moves(bitboards, white_to_move, False)
    queen_moves = get_queen_moves(bitboards, white_to_move)
    king_moves = get_king_moves(bitboards, white_to_move, castling)

    all_moves = pawn_moves + knight_moves + bishop_moves + rook_moves + queen_moves + king_moves

    return all_moves


#TODO Promotion
def get_all_legal_moves(game : Game) -> list[Move]:
    """Finds all legal moves in a position.

    Args:
        game (Game): The game state.

    Returns:
        list[Move]: All legal moves.
    """
    all_legal_moves = []
    all_possible_moves = get_all_possible_moves(game.bitboards, game.en_passant_square[-1], game.white_to_move, 
                                                {"wkk" : game.wk_can_kingside_castle[-1], "wkq" : game.wk_can_queenside_castle[-1], 
                                                 "bkk" : game.bk_can_kingside_castle[-1], "bkq" : game.bk_can_queenside_castle[-1]})
    for move in all_possible_moves:
        game.make_move(move)
        ennemy_moves = get_all_possible_moves(game.bitboards, game.en_passant_square[-1], game.white_to_move, 
                                            {"wkk" : game.wk_can_kingside_castle[-1], "wkq" : game.wk_can_queenside_castle[-1], 
                                             "bkk" : game.bk_can_kingside_castle[-1], "bkq" : game.bk_can_queenside_castle[-1]})
        
        if not game.white_to_move and not move.is_castling_move:
            _, king_i, king_j = find_coordinates(game.bitboards["wK"])[0]
        elif game.white_to_move and not move.is_castling_move:
            _, king_i, king_j = find_coordinates(game.bitboards["bK"])[0]
        else:
            king_i, king_j = move.init_square 

        game.undo_move()

        to_add = True
        for ennemy_move in ennemy_moves:
            if ennemy_move.final_square == (king_i, king_j):
                to_add = False
                break
        
        if to_add:
            all_legal_moves.append(move)

    return all_legal_moves
