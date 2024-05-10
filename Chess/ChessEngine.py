###   !!! TODO: can't yet castle !!!    ###


"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state.
It will also keep a move log.
"""
class GameState():
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characers.
        # The first character represents the colour of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N' or 'p'
        # "--" - represents an empty space with no piece.
        # NB using numpy array might be more efficient
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "wP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"P":self.getPawnMoves, "R":self.getRookMoves, "N":self.getKnightMoves,
                              "B":self.getBishopMoves, "Q":self.getQueenMoves, "K":self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # coordinates for the square where en passant is possible


    '''
    Takes a move as a parameter and executes it. This will not work for castling, en passant and pawn promotion
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later
        turn = "W: " if self.whiteToMove else "B: "
        print(turn + move.pieceMoved[1]+move.getRankFile(move.endRow, move.endCol))
        self.whiteToMove = not self.whiteToMove # swap players
        # update king's position if needed
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            move.promotionChoice = move.getPromotionChoice()
            print(move.pieceMoved[1] + move.getRankFile(move.endRow,move.endCol) + " is now " + move.promotionChoice + move.getRankFile(move.endRow, move.endCol))
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionChoice


        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the pawn

        # update enpassantPossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:   # only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()


    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            print(self.moveLog[len(self.moveLog)-1].pieceMoved[1]+self.moveLog[len(self.moveLog)-1].getRankFile(self.moveLog[len(self.moveLog)-1].endRow, self.moveLog[len(self.moveLog)-1].endCol)+" undone")
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update king's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                print(move.pieceCaptured)
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo a 2 square pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # squares that piece can move to
                # if knight, must capture knight or move king. Other pieces can be blocked.
                if pieceChecking == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, len(self.board)):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you get to piece and checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])

            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        return moves


    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy can attack the square r,c
    '''
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turn back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:  # square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):                              # number of rows
            for col in range(len(self.board[row])):                     # number of cols in given row
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)          # calls the appropriate move function
        return moves

    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:                                            # white pawn moves
            if self.board[row-1][col] == "--":                          # 1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row, col), (row-1, col), self.board))
                    if row == 6 and self.board[row-2][col] == "--":     # 2 square pawn advance
                        moves.append(Move((row, col), (row-2, col), self.board))
            if col-1 >= 0:                                              # captures to the left
                if self.board[row-1][col-1][0] != self.board[row][col][0] and self.board[row-1][col-1][0] != "-":
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantMove=True))
            if col+1 < len(self.board[0]):                              # captures to the right
                if self.board[row-1][col+1][0] != self.board[row][col][0] and self.board[row-1][col+1][0] != "-":
                    if not piecePinned or pinDirection == (-1, +1):
                        moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantMove=True))

        else:                                                           # black pawn moves
            if self.board[row+1][col] == "--":                          # 1 square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row, col), (row+1, col), self.board))
                    if row == 1 and self.board[row+2][col] == "--":     # 2 square pawn advance
                        moves.append(Move((row, col), (row+2, col), self.board))
            if col-1 >= 0:                                              # captures to the left
                if self.board[row+1][col-1][0] != self.board[row][col][0] and self.board[row+1][col-1][0] != "-":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row, col), (row+1, col-1), self.board))
                elif (row+1, col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row+1, col-1), self.board, isEnpassantMove=True))
            if col+1 < len(self.board[0]):                              # captures to the right
                if self.board[row+1][col+1][0] != self.board[row][col][0] and self.board[row+1][col+1][0] != "-":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row, col), (row+1, col+1), self.board))
                elif (row+1, col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row+1, col+1), self.board, isEnpassantMove=True))


    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':  # you can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        for i in range(-1,2):                                                                           # moves left/right
            for j in range(-1,2):
                if abs(i) + abs(j) == 2:
                    pass
                else:
                    n = 1
                    while 0 <= row + i*n < len(self.board) and 0 <= col + j*n < len(self.board[0]) and self.board[row + i*n][col + j*n] == "--":                  # moves
                        if not piecePinned or pinDirection == (i, j) or pinDirection == (-i, -j):
                            moves.append(Move((row, col), (row + i*n, col + j*n), self.board))
                        n += 1
                    if 0 <= row + i*n < len(self.board) and 0 <= col + j*n < len(self.board[0]) and self.board[row + i*n][col + j*n][0] != self.board[row][col][0]:   # captures
                        if not piecePinned or pinDirection == (i, j) or pinDirection == (-i, -j):
                            moves.append(Move((row, col), (row + i*n, col + j*n), self.board))


    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''
    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        for i in range(-1, 2):                                                                           # moves left/right
            for j in range(-1, 2):
                if i == 0 or j == 0:
                    pass
                else:
                    n = 1
                    while 0 <= row + i*n < len(self.board) and 0 <= col + j*n < len(self.board[0]) and self.board[row + i*n][col + j*n] == "--":         # moves diagonally up and left
                        if not piecePinned or pinDirection == (i, j) or pinDirection == (-i, -j):
                            moves.append(Move((row, col), (row + i*n, col + j*n), self.board))
                        n += 1
                    if 0 <= row + i*n < len(self.board) and 0 <= col + j*n < len(self.board[0]) and self.board[row+i*n][col+j*n][0] != self.board[row][col][0]:          # captures diagonally up and left
                        if not piecePinned or pinDirection == (i, j) or pinDirection == (-i, -j):
                            moves.append(Move((row, col), (row + i*n, col + j*n), self.board))

    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''
    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        for i in range(-2, 3):
            for j in range(-2, 3):
                if abs(i) == abs(j) or i == 0 or j == 0:
                    pass
                else:
                    if 0 <= row+i < len(self.board) and 0 <= col+j < len(self.board[0]) and self.board[row+i][col+j][0] != self.board[row][col][0]:
                        if not piecePinned:
                            moves.append(Move((row, col), (row+i, col+j), self.board))
    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''
    def getQueenMoves(self, row, col, moves):
        # pass
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''
    def getKingMoves(self, row, col, moves):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if abs(i) + abs(j) == 0:                            # moving to your own square is not a move
                    pass
                elif 0 <= row + i < len(self.board) and 0 <= col + j < len(self.board[0]) and self.board[row+i][col+j][0] != self.board[row][col][0]:
                    if self.whiteToMove:
                        self.whiteKingLocation = (row+i, col+j)
                    else:
                        self.blackKingLocation = (row+i, col+j)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row,col), (row+i, col+j), self.board))
                    # place king back on original square
                    if self.whiteToMove:
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    '''
    Returns if the player is in check, a list of pins and a list of checks
    '''
    def checkForPinsAndChecks(self):
        pins = [] # squares where the allied pinned piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColour = "b"
            allyColour = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColour = "w"
            allyColour = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, len(self.board)):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board):
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColour and endPiece[1] != 'K':
                        if possiblePin == ():   # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:                   # 2nd allied piece, so no pin or check possible
                            break
                    elif endPiece[0] == enemyColour:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1. orthogonally away from king and piece is a rook
                        # 2. diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColour == 'w' and 6 <= j <= 7) or (enemyColour == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or \
                                (i == 1 and type == 'K'):
                            if possiblePin == ():   # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:                   # piece blocking, so pin
                                pins.append(possiblePin)
                                break
                        else:                       # enemy piece not applying check
                            break
                else:
                    break                           # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColour and endPiece[1] == 'N':  # enemy knight attacking the king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks



'''
This class is responsible for handling all the information relating to a single move
'''
class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion info
        self.isPawnPromotion = False
        self.promotionChoice = "Q"
        self.isPawnPromotion = ((self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7))
        # enpassant info
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        self.moveID = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol


    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + " -> " + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]


    def getPromotionChoice(self):
        self.promotionChoice = input("Pawn promotion! What piece would you like to promote to: Q, R, N or B? ")
        if self.promotionChoice in ["Q", "R", "N", "B"]:
            pass
        else:
            print("Please type one of Q, R, N or B (case sensitive)")
            self.getPromotionChoice()
        return self.promotionChoice
