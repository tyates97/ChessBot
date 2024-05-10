"""
This will be our main driver file. It will be responsible for handling our user input and displaying the current GameState
"""
import pygame
import pygame as p
from Chess import ChessEngine

p.init()
WIDTH = HEIGHT = 512    # 400 is another option
DIMENSION = 8           # dimensions of a chessboard are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15            # for animations later on
IMAGES = {}


'''
Initialise a global dictionary of images. This will be called exactly once in the main
'''
def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying 'IMAGES['wP']'


'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False        # flag variable for when a move is made
    loadImages()            # only do this once, before the while loop
    running = True
    sqSelected = ()         # no square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = []       # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()            # (x,y) location of the mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):            # the user clicked the same square twice
                    sqSelected = ()                     # deselect
                    playerClicks = []                   # clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)     # append for both first and second clicks
                if len(playerClicks) == 2:              # after 2nd click
                    if gs.board[playerClicks[0][0]][playerClicks[0][1]] == "--" or gs.board[playerClicks[0][0]][playerClicks[0][1]][0] == gs.board[playerClicks[1][0]][playerClicks[1][1]][0]:  # if the player clicks one piece then another on their side, select piece 2
                        sqSelected = playerClicks[1]
                        playerClicks = [playerClicks[1]]
                        break
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()                     # reset userClicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Responsible for all the graphics within a current game state
'''
def drawGameState(screen, gs, sqSelected):
    drawBoard(screen, sqSelected)   # draw squares on the board
    # add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board) # draw pieces on top of those squares


'''
Draw the squares on the board.
'''
def drawBoard(screen, sqSelected):
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            if (row, column) == sqSelected:
                p.draw.rect(screen, p.Color("red"), pygame.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, colors[(row + column)%2], pygame.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the pieces on the board using the current game state's board variable
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--": # not empty square
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()

