import pygame
import webbrowser

boardWidth = boardHeight = 600
boardDimension = 8
squareSize = boardHeight // boardDimension
chessPieces = {}

# initialize a global directory of images to be called exactly once in the main.
def loadImages():

    # loop through each piece, load it and scale it
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        chessPieces[piece] = pygame.transform.scale(pygame.image.load("pieces/" + piece + ".png"), (squareSize, squareSize))

# main game function/handling user input
def main():
    
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    gameState = GameState()
    validMoves = gameState.getValidMoves()
    isMoveMade = False  # flag variable for when a move is made, keep track to generate new valid moves
    loadImages()  # do this only once before while loop
    running = True
    selectedSquare = ()  # no square is selected initially, this will keep track of the last click of the user 
    playerClicks = []  # this will keep track of player clicks 
    gameOver = False

    while running:
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            # mouse handler, get the position of the selected square
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = pygame.mouse.get_pos()  # (x, y) location of the mouse
                    column = location[0] // squareSize
                    row = location[1] // squareSize
                    if selectedSquare == (row, column) or column >= 8:  # user clicked the same square twice
                        selectedSquare = ()  # deselect
                        playerClicks = []  # clear clicks
                    # store the selected square
                    else:
                        selectedSquare = (row, column)
                        playerClicks.append(selectedSquare)  
                    # make the move
                    if len(playerClicks) == 2:  # after 2nd click
                        move = Move(playerClicks[0], playerClicks[1], gameState.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gameState.makeMove(validMoves[i])
                                isMoveMade = True
                                selectedSquare = ()  # reset user clicks
                                playerClicks = []
                        if not isMoveMade:
                            playerClicks = [selectedSquare]
            # key handler
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:  # undo when 'z' is pressed
                    gameState.undoMove()
                    isMoveMade = True
                    gameOver = False
                if event.key == pygame.K_r:  # reset the game when 'r' is pressed, add a way back to the menu straight from the gave over screen after patching the AI
                    gameState = GameState()
                    validMoves = gameState.getValidMoves()
                    selectedSquare = ()
                    playerClicks = []
                    isMoveMade = False
                    gameOver = False
                
        if isMoveMade:
            # generate a new set of valid moves
            validMoves = gameState.getValidMoves()
            isMoveMade = False

        drawGameState(screen, gameState, validMoves, selectedSquare)        

        if gameState.checkmate:
            gameOver = True
            if gameState.whiteToMove:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif gameState.stalemate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")
        pygame.display.flip()


def drawGameState(screen, gameState, validMoves, selectedSquare):

    drawBoard(screen)  # draw squares on the board
    drawPieces(screen, gameState.board)  # draw pieces on top of those squares
    highlightSquares(screen, gameState, validMoves, selectedSquare)

      
def highlightSquares(screen, gameState, validMoves, selectedSquare):
 
    if (len(gameState.moveLog)) > 0:
        lastMove = gameState.moveLog[-1]
        screen2 = pygame.Surface((squareSize, squareSize))
        screen2.set_alpha(100)
        screen2.fill(pygame.Color(10, 255, 255))
        screen.blit(screen2, (lastMove.end_col * squareSize, lastMove.end_row * squareSize))
    if selectedSquare != ():
        row = selectedSquare[0]
        column = selectedSquare[1]
        if gameState.board[row][column][0] == ('w' if gameState.whiteToMove else 'b'): 
            # highlight selected square
            screen2 = pygame.Surface((squareSize, squareSize))
            screen2.set_alpha(100)  # transparency (0 is transparent, 255 opaque)
            screen2.fill(pygame.Color(175, 225, 175))
            screen.blit(screen2, (column * squareSize, row * squareSize))
            # highlight moves from that square
            screen2.fill(pygame.Color('yellow'))
            for move in validMoves:
                if move.start_row == row and move.start_col == column:
                    screen.blit(screen2, (move.end_col * squareSize, move.end_row * squareSize))
    
# draw the board
def drawBoard(screen):
 
    global colors
    colors = [pygame.Color("white"), pygame.Color(222,184,135)]
    for row in range(boardDimension):
        for column in range(boardDimension):
            color = colors[((row + column) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(column * squareSize, row * squareSize, squareSize, squareSize))

# draw the chess pieces
def drawPieces(screen, board):
 
    for row in range(boardDimension):
        for column in range(boardDimension):
            piece = board[row][column]
            if piece != "--":
                screen.blit(chessPieces[piece], pygame.Rect(column * squareSize, row * squareSize, squareSize, squareSize))

# displaying game result when the game is over
def drawEndGameText(screen, text):
    checkmate = buttonFont.render(text, False, pygame.Color("grey"))
    textLocation = pygame.Rect(0, 0, boardWidth, boardHeight).move(boardWidth/2 - checkmate.get_width()/2, boardHeight/2 - checkmate.get_height()/2)
    screen.blit(checkmate, textLocation)
    stalemate = buttonFont.render(text, False, pygame.Color('black'))
    screen.blit(stalemate, textLocation.move(2, 2))

 # class responsible for most game functions
class GameState:

    def __init__(self):

        # the first character of each index represents the colour of the piece
        # the second character of each index respresents the type of the piece
        # empty squares are represented by two dashes

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True # white always makes the first move
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # coordinates for the square where en-passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    # allow the player to make a move
    def makeMove(self, move):
  
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # switch players
        # update king's location if moved, important to check castling rights
        if move.piece_moved == "wK":
            self.whiteKingLocation = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            # if not is_AI:
            #    promoted_piece = input("Promote to Q, R, B, or N:") #take this to UI later
            #    self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            # else:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # enpassant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"  # capturing the pawn

        # update enpassant_possible variable
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advance
            self.enpassantPossible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # kingside castle move
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # moves the rook 
                self.board[move.end_row][move.end_col + 1] = '--'  # erase old rook
            else:  # queenside castle 
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # moves the rook 
                self.board[move.end_row][move.end_col - 2] = '--'  # erase old rook

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # update castling rights 
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    def undoMove(self):

        # undo the last move, can be done multiple times
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove  # swap players
            # update the king's position if needed
            if move.piece_moved == "wK":
                self.whiteKingLocation = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            # undo en passant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # undo castle rights
            self.castleRightsLog.pop()  # get rid of the new castle rights from the move we are undoing
            self.currentCastlingRights = self.castleRightsLog[
                -1]  # set the current castle rights to the last one in the list
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move
        """
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.currentCastlingRights.wqs = False
            elif move.end_col == 7:  # right rook
                self.currentCastlingRights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.currentCastlingRights.bqs = False
            elif move.end_col == 7:  # right rook
                self.currentCastlingRights.bks = False

        if move.piece_moved == 'wK':
            self.currentCastlingRights.wqs = False
            self.currentCastlingRights.wks = False
        elif move.piece_moved == 'bK':
            self.currentCastlingRights.bqs = False
            self.currentCastlingRights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                          self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # advanced algorithm
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            king_row = self.whiteKingLocation[0]
            king_col = self.whiteKingLocation[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

        # if no moves can be made then it is checkmate
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            # moves can be made by the other player, it is just not their turn when it is stalemate
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.currentCastlingRights = temp_castle_rights
        return moves

    def inCheck(self):
        """
        Determine if a current player is in check
        """
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])

    def squareUnderAttack(self, row, col):
        """
        Determine if enemy can attack the square row col
        """
        self.whiteToMove = not self.whiteToMove  # switch to opponent's point of view
        opponents_moves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def getAllPossibleMoves(self):
        """
        All moves without considering checks.
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)  # calls appropriate move function based on piece type
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKingLocation[0]
            start_col = self.whiteKingLocation[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def getPawnMoves(self, row, col, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.whiteKingLocation
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_location

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, is_enpassant_move=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.enpassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, is_enpassant_move=True))

    def getRookMoves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][
                    1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check for possible moves only in boundaries of the board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2),
                        (1, -2))  # up/left up/right right/up right/down down/left down/right left/up left/down
        ally_color = "w" if self.whiteToMove else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # so its either enemy piece or empty square
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def getBishopMoves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        """
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.black_king_location = (row, col)

    def getCastleMoves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # in chess, fields on the board are described by two symbols, one of them being number between 1-8 (which is corresponding to rows)
    # and the second one being a letter between a-f (corresponding to columns), in order to use this notation we need to map our [row][col] coordinates
    # to match the ones used in the original chess game
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (
                self.piece_moved == "bp" and self.end_row == 7)
        # en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"
        # castle move
        self.is_castle_move = is_castle_move

        self.is_capture = self.piece_captured != "--"
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """
        Overriding the equals method.
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        if self.is_pawn_promotion:
            return self.getRankFile(self.end_row, self.end_col) + "Q"
        if self.is_castle_move:
            if self.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.is_enpassant_move:
            return self.getRankFile(self.start_row, self.start_col)[0] + "x" + self.getRankFile(self.end_row,
                                                                                                self.end_col) + " e.p."
        if self.piece_captured != "--":
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.start_row, self.start_col)[0] + "x" + self.getRankFile(self.end_row,
                                                                                                    self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.getRankFile(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.getRankFile(self.end_row, self.end_col)

        # TODO Disambiguating moves

    def getRankFile(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def __str__(self):
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.getRankFile(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square

# create display window

screenWidth = 800
screenHeight = 600

icon = pygame.image.load("icons/chessIcon.jpg")
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("")

# menu state

menuState = "main" 

# define fonts

titleFont = pygame.font.Font("fonts/titleFont.ttf", 70)
buttonFont = pygame.font.Font("fonts/buttonFont.ttf", 22)

# define colours

textColour = (255, 255, 255)

# import sounds/music

buttonSound = pygame.mixer.Sound("sounds/buttonPressSound.mp3")
linkSound = pygame.mixer.Sound("sounds/linkButtonSound.mp3")

pygame.mixer.music.load("music/mainMusic.mp3")
pygame.mixer.music.play(-1)

# display text on screen

def blitText(surface, text, pos, font, colour=pygame.Color("black")):

    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words
    space = font.size(' ')[0]  # the width of a space
    maxWidth, maxHeight = surface.get_size()
    x, y = pos

    for line in words:
        for word in line:
            wordSurface = font.render(word, 0, colour)
            wordWidth, wordHeight = wordSurface.get_size()
            if x + wordWidth >= maxWidth: 
                x = pos[0]  # reset the x
                y += wordHeight  # start on a new row
            surface.blit(wordSurface, (x, y))
            x += wordWidth + space
        x = pos[0]  # reset the x again
        y += wordHeight  # start on a new row again


information = ("Chess is a game played between two opponents on opposite sides of a board containing\n"\
                    "64 squares of alternating colours; black and white. Each player has 16 pieces: 1 king,\n1 queen, 2 rooks, "\
                    "2 bishops, 2 knights, and 8 pawns. The goal of the game is to \ncheckmate the other king. "\
                    "To help you understand how each of the pieces move, the\nrules, and how to win, I have "\
                    "included some links to sources of information that I found helpful as a beginner. Good luck, have fun playing, and "\
                    "enjoy your chess journey!")

# game title

title = titleFont.render("Chess.exe", True, "white")
titleRect = title.get_rect()
titleRect.center = (screenWidth/2, 100)

# button class

class Button():

    def __init__(self, image, xPos, yPos, text_input):

        self.image = image
        self.x = xPos 
        self.y = yPos
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_input = text_input
        self.text = buttonFont.render(self.text_input, True, "white")
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def update(self):

        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):

        action = False
        pos = pygame.mouse.get_pos() 

        if self.rect.collidepoint(pos):
            print("pressed") # to ensure that all buttons, regardless of functionallity respond to input
            action = True
        return action

# load button images/images and buttons

playButton = pygame.image.load("buttons/playButton.png")
playButton = Button(playButton, 400, 300, "")

optionsMenuButton = pygame.image.load("buttons/optionsMenuButton.png")
optionsMenuButton = Button(optionsMenuButton, 400, 370, "")

helpButton = pygame.image.load("buttons/helpButton.png")
helpButton = Button(helpButton, 400, 440, "")

mainMenuButton = pygame.image.load("buttons/mainMenuButton.png")
mainMenuButton = Button(mainMenuButton, 400, 520, "")

helpMenuBackground = pygame.image.load("backgrounds/helpMenuBackground.jpg")
helpMenuBackground = pygame.transform.scale(helpMenuBackground, (screenWidth, screenHeight))

mainMenuBackGround = pygame.image.load("backgrounds/mainMenuBackground.jpg")
mainMenuBackground = pygame.transform.scale(mainMenuBackGround, (screenWidth, screenHeight))

optionsMenuBackground = pygame.image.load("backgrounds/optionsMenuBackground.jpg")
optionsMenuBackground = pygame.transform.scale(optionsMenuBackground, (screenWidth, screenHeight))

# main game loop

run = True
while run:

    if menuState == "main":

        #display background

        screen.blit(mainMenuBackground, (0, 0))
        screen.blit(title, titleRect)

        # event handler

        for event in pygame.event.get():

            if event.type == pygame.QUIT:   
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.checkForInput(pygame.mouse.get_pos()):
                    menuState = "play"
                    buttonSound.play()
                if optionsMenuButton.checkForInput(pygame.mouse.get_pos()):
                    menuState = "options"
                    buttonSound.play()
                if helpButton.checkForInput(pygame.mouse.get_pos()):
                    menuState = "help"
                    buttonSound.play()

        playButton.update()
        optionsMenuButton.update()
        helpButton.update()
        
    elif menuState == "options":

        screen.blit(optionsMenuBackground, (0, 0))
            
        # event handler
        
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mainMenuButton.checkForInput(pygame.mouse.get_pos()):
                    menuState = "main"
                    buttonSound.play()
        
        mainMenuButton.update()

    elif menuState == "help":
    
        screen.blit(helpMenuBackground, (0, 0))
        blitText(screen, information, (20, 40), buttonFont)

        # links

        howToPlayChessLink = screen.blit(buttonFont.render("• How To Play Chess | Chess.com", True, "navy blue"), (20, 240))
        howToMoveThePiecesLink = screen.blit(buttonFont.render("• How To Move The Pieces | Chess.com", True, "navy blue"), (20, 270))
        beginnersGuideToChess = screen.blit(buttonFont.render("• Beginners Guide To Chess | Lichess", True, "navy blue"), (20, 300))
        saintLouisChessClub = screen.blit(buttonFont.render("• Saint louis Chess Club | Youtube", True, "navy blue"), (20, 330))
        chessManiac = screen.blit(buttonFont.render("• Free Chess Ebooks | Chess Maniac", True, "navy blue"), (20, 360))
        redditChess = screen.blit(buttonFont.render("• r/chess | Reddit", True, "navy blue"), (20, 390))
        theWeekInChess = screen.blit(buttonFont.render("• Daily Chess News & Games| The Week in Chess", True, "navy blue"), (20, 420))
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mainMenuButton.checkForInput(pygame.mouse.get_pos()):
                    menuState = "main"
                    buttonSound.play()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if howToPlayChessLink.collidepoint(pos):
                    webbrowser.open(r"https://www.chess.com/article/view/how-to-play-chess")
                    linkSound.play()
                if howToMoveThePiecesLink.collidepoint(pos):
                    webbrowser.open(r"https://www.chess.com/article/view/how-to-move-the-pieces")
                    linkSound.play()
                if beginnersGuideToChess.collidepoint(pos):
                    webbrowser.open(r"https://lichess.org/study/oFHnjHO0/J1ez3o9R")
                    linkSound.play()
                if saintLouisChessClub.collidepoint(pos):
                    webbrowser.open(r"https://www.youtube.com/channel/UCM-ONC2bCHytG2mYtKDmIeA")
                    linkSound.play()
                if chessManiac.collidepoint(pos):
                    webbrowser.open(r"https://www.chessmaniac.com/chess_ebooks/")
                    linkSound.play()
                if redditChess.collidepoint(pos):
                    webbrowser.open(r"https://www.reddit.com/r/chess/")
                    linkSound.play()
                if theWeekInChess.collidepoint(pos):
                    webbrowser.open(r"https://theweekinchess.com/live")
                    linkSound.play()
            
        mainMenuButton.update()

    elif menuState == "play":
        pygame.mixer.music.fadeout(3000)
        main()
        
        
    pygame.display.update()
    
pygame.quit()
