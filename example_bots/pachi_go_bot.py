from pydantic import BaseModel
from typing import Optional, List, Dict
import subprocess
import threading
import time
import re 
import numpy as np 
from typing import List, Union
from basebot import BaseBotWithLocalDb
from basebot.models.the_message import MessageWrapper


from PIL import Image, ImageDraw, ImageFont




BOARD_SIZE = 19
KOMI = 7.5

class IllegalMoveException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class PachiMoveRequest(BaseModel):
    moves: list
    bot_color: str

class PachiMoveResponse(BaseModel):
    board_state: List[list]
    moves: list
    black_captures: int
    white_captures: int
    invalid_last_move: Optional[bool] = False
    winner: Optional[str] = None
    black_territory: Optional[list] = None
    white_territory: Optional[list] = None


def parse_territory(resp):
    positions = [p for p in resp.split(' ') if p and p != '=']
    return positions


class PachiGo:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.p = subprocess.Popen(["pachi", "-t", "~500", "-s", "5", "-D", "--log-file", "pachi.logs" ],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        time.sleep(0.5)
        self.send_command("boardsize %d" % BOARD_SIZE)
        self.send_command("komi %f" % KOMI)

    def get_board(self):
        cmd = "showboard"
        cmd = cmd.encode('utf-8') + b'\n'
        self.p.stdin.write(cmd)
        self.p.stdin.flush()
        captures = None
        succeeded = False
        started = False
        idx = 0
        board_state = np.zeros((BOARD_SIZE, BOARD_SIZE)).astype(np.int32)
        while not succeeded:
            line = self.p.stdout.readline().decode('utf-8')
            
            print({'idx':str(idx).zfill(2) , 'line': line})
            if line[0] == '=':
                started = True
            elif line[0] == '' or line[0] == '\n':
                succeeded = True
            if started:
                line = line.strip()
                if captures is None:
                    captures_str = line.split()[4:]
                    # print('captureds_list',type(captures_str), captures_str)
                    capb = int(captures_str[5])
                    capw = int(captures_str[7])
                    captures = [capb, capw]
                else:
                    try:
                        # print(':3', line[:3], '"')
                        if line[:3] in ['A B', '+--']:
                            continue
                        y = int(line[:2]) - 1
                        # print('Y=',y)
                        x = 0
                        started = False
                        for c in line:
                            if c == '|' and started:
                                break
                            elif c == '|':
                                started = True
                            if c and started:
                                if c == '.':
                                    board_state[x,y] = 0
                                    x += 1
                                elif c == 'X':
                                    board_state[x,y] = 1
                                    # print('Black=', (x,y))
                                    x += 1
                                elif c == 'O':
                                    # print('White=', (x,y))
                                    board_state[x,y] = -1
                                    x += 1
                    except Exception as e:
                        # print('skipping')
                        pass
                idx += 1
        return board_state.tolist(), captures

    def get_response(self):
        # print('in get response')
        succeeded = False
        started = False
        result = ''
        while not succeeded:
            line = self.p.stdout.readline().decode('utf-8')
            # print({'line': line})
            if line[0] == '=' or line[0] == '?':
                started = True
            elif line[0] == '' or line[0] == '\n':
                succeeded = True
            if started:
                line = line.strip()
                result += re.sub('^= ?', '', line)
        return result

    def send_command(self, cmd, move=False):
        cmd = cmd.encode('utf-8') + b'\n'
        self.p.stdin.write(cmd)
        self.p.stdin.flush()
        if move:
            time.sleep(1)
            pass
        response = self.get_response()
        p_stderr = None
        if self.p.stderr:
            p_stderr = self.p.stderr.read().decode().strip()
            print('StdErr:', self.p.stderr, self.p.stdout.readline().decode().strip(), vars(self.p))
        return response, p_stderr

    def get_pachi_move(self, prior_moves=[], pachi_color='b'):
        self.send_command("clear_board")
        for move in prior_moves:
            color, mv = move
            resp, err = self.send_command(f"play {color} {mv}")
            print('move', move, 'resp:', resp, 'err:', err)
            if 'illegal move' in resp:
                raise IllegalMoveException()

        # Get Pachi's move
        response, error = self.send_command(f"genmove {pachi_color}", move=True)
        if error:
            print("Pachi error:", error)
            return None
        if response.endswith('pass'):
            return response, None # Pachi passes
        return response

    def finish_game(self, prior_moves=[]):
        self.send_command("clear_board")
        for move in prior_moves:
            color, mv = move
            self.send_command(f"play {color} {mv}")
        winner, error = self.send_command('score_est')
        black_territory, err = self.send_command('final_status_list black_territory')
        black_territory = parse_territory(black_territory)
        white_territory, err = self.send_command('final_status_list white_territory')
        white_territory = parse_territory(white_territory)
        return winner, black_territory, white_territory

    def genmove(self, request: PachiMoveRequest) -> PachiMoveResponse:
        try:
            self.lock.acquire()
            winner = None 
            black_territory = None
            white_territory = None
            invalid_move = False
            if request.moves[-1][1] == 'pass':
                # finish game logic
                winner, black_territory, white_territory = self.finish_game(prior_moves=request.moves)
                moves = request.moves
                moves.append([request.bot_color, 'pass'])
            else:
                move = self.get_pachi_move(request.moves, pachi_color=request.bot_color)
                moves = request.moves
                moves.append([request.bot_color, move])
            board, captures = self.get_board()
            self.lock.release()
        except IllegalMoveException as e:
            board, captures = self.get_board()
            self.lock.release()
            moves = []
            invalid_move = True
        except Exception as e:
            self.lock.release()
            raise(e)
        return PachiMoveResponse(board_state=board, moves=moves, black_captures=captures[0], white_captures=captures[1], 
                                winner=winner, black_territory=black_territory, white_territory=white_territory,
                                invalid_last_move=invalid_move)




BOARD_STATE = 'board_state'

board_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
board_letters_to_num = {}
for i in range(len(board_letters)):
    board_letters_to_num[board_letters[i]] = i

def draw_go_board(board_size):
    # Set the dimensions of the board and the spacing between the lines
    board_width = 600
    line_width = board_width // (board_size + 1)

    # Create a new image with a white background
    img = Image.new("RGB", (board_width, board_width), "yellow")

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Draw the horizontal lines
    for i in range(board_size):
        y = (i + 1) * line_width
        draw.line((line_width, y, board_width - line_width, y), fill=0, width=2)

    # Draw the vertical lines
    for i in range(board_size):
        x = (i + 1) * line_width
        draw.line((x, line_width, x, board_width - line_width), fill=0, width=2)

    # Draw the star points (if board size is larger than 11)
    if board_size >= 11:
        star_points = [(4,4), (4,board_size-3), (board_size-3,4), 
                       (board_size-3,board_size-3), 
                       ((board_size+1)//2, (board_size+1)//2),
                       (4,(board_size+1)//2), (board_size-3,(board_size+1)//2), 
                       ((board_size+1)//2,4), ((board_size+1)//2,board_size-3)]
        for point in star_points:
            x, y = point
            draw.rectangle((x*line_width-2, y*line_width-2, x*line_width+2, y*line_width+2), fill=0)

    font = ImageFont.truetype('/usr/share/fonts/truetype/Arialbd.TTF', size=14)
    # Draw the labels on the x-axis (letters)
    for i in range(board_size):
        x = (i + 1) * line_width
        # draw.text((x - 2, 10), chr(ord('A')+i), fill=0, font=font)
        draw.text((x - 3, 10), board_letters[i], fill=0, font=font)
        draw.text((x - 3, board_width-18), board_letters[i], fill=0, font=font)

    # Draw the labels on the y-axis (numbers)
    for i in range(board_size):
        y = (i + 1) * line_width
        draw.text((10, y - 5), str(i+1), fill=0, font=font)
        draw.text((board_width-18, y - 5), str(i+1), fill=0, font=font)

    # Show the image
    return img


def add_stone_to_board(board_image, stone_position, stone_color, emphasize=False, small=False):
    # Get the dimensions of the board image and calculate the spacing between the lines
    board_width, board_height = board_image.size
    line_width = board_width // (BOARD_SIZE + 1)

    # Calculate the position of the stone on the board
    x, y = stone_position
    stone_x = (x + 1) * line_width
    stone_y = (y + 1) * line_width

    outline = 'black'
    if emphasize:
        outline = 'red'
    # Create a drawing context
    draw = ImageDraw.Draw(board_image)

    # Draw the stone on the board
    if stone_color == "black":
        if small:
            draw.ellipse((stone_x - 0.2 * line_width, stone_y - 0.2 * line_width,
                      stone_x + 0.2 * line_width, stone_y + 0.2 * line_width), fill="black", outline=outline)
        else:
            draw.ellipse((stone_x - 0.5 * line_width, stone_y - 0.5 * line_width,
                      stone_x + 0.5 * line_width, stone_y + 0.5 * line_width), fill="black", outline=outline)
    elif stone_color == "white":
        if small:
            draw.ellipse((stone_x - 0.2 * line_width, stone_y - 0.2 * line_width,
                        stone_x + 0.2 * line_width, stone_y + 0.2 * line_width), fill="white", outline=outline)
        else:
            draw.ellipse((stone_x - 0.5 * line_width, stone_y - 0.5 * line_width,
                        stone_x + 0.5 * line_width, stone_y + 0.5 * line_width), fill="white", outline=outline)

    # Show the updated board image
    # board_image.show()

def to_position(n,c):
    x = board_letters_to_num[c.upper()]
    y = n - 1
    return (x, y)
    


class GoBot(BaseBotWithLocalDb):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('starting PachiGo. Warning this will fail (possibly silently) if you dont have it installed.')
        self.pachi = PachiGo()
    def help(self) -> str:
        return 'Play your moves like so: D4. When you pass the game automatically ends and is scored. You can start a new game without finishing your last game.'
    def templates(self, user_id=None):
        return [
            'Start game',
            'Pass',
        ]
    
    def parse_move(self, txt:str):
        txt = txt.strip()
        a1 = txt[0]
        a2 = txt[1:]
        try:
            c = a1.upper()
            n = int(a2)
            return to_position(n, c)
        except Exception as e:
            try:
                n = int(a1)
                c = a2.upper()
                return to_position(n, c)
            except Exception as e:
                return None
        return None
    
    def draw_board(self, board:List[list], last_move=None):
        if last_move is None:
            last_move = [-1, -1]
        size = len(board)
        img = draw_go_board(BOARD_SIZE)
        for x in range(size):
            for y in range(size):
                if board[x][y] == 1:
                    add_stone_to_board(img, (x,y), stone_color='black',emphasize=(last_move[0] == x and last_move[1] == y))
                elif board[x][y] == -1:
                    add_stone_to_board(img, (x,y), stone_color='white',emphasize=(last_move[0] == x and last_move[1] == y))
        return img
    
    def draw_endgame_board(self, board:List[list], black_territory:list, white_territory:list):
        img = self.draw_board(board)
        for pt in black_territory:
            x,y = to_position(int(pt[1:]), pt[0].upper())
            add_stone_to_board(img, (x,y), stone_color='black', small=True)
            pass 
        for pt in white_territory:
            x,y = to_position(int(pt[1:]), pt[0].upper())
            add_stone_to_board(img, (x,y), stone_color='white', small=True)
            pass
        return img
    
    def respond(self, message: MessageWrapper):
        resp_msg = self.get_message_to(message.get_sender_id())
        if message.get_text().strip().lower() == 'start game':
            board_state = {'moves': [] }
            print('BOARD STATE', board_state)
            resp_msg.set_extra_property(BOARD_STATE, board_state)
            board_image = self.draw_board(board=[])
            resp_msg.set_images_pil([board_image])
            return resp_msg

        prev_msgs = self.get_message_context(message=message, limit=8, descending=True)
        board_state = None
        for msg in prev_msgs:
            if msg.get_sender_id() == self.bot_id and msg.get_from_extras(BOARD_STATE):
                board_state = msg.get_from_extras(BOARD_STATE)
                break
        if board_state:
            moves = board_state['moves']
            if len(moves) > 1 and moves[-1][1] == 'pass':
                resp_msg.set_text("Game is finished. Start a new game.")
                return resp_msg
            move_txt = message.get_text().strip()
            if move_txt.lower() == 'resign':
                # RESIGN logic
                # game_state = game_state.apply_move(Move.resign())
                print('TODO figure out resign')
                pass
            elif move_txt.lower() == 'pass' or self.parse_move(message.get_text()):
                move = message.get_text().strip()
                if move.lower() == 'pass':
                    move = move.lower()
                moves.append(('b', move))
                bot_move = self.pachi.genmove(PachiMoveRequest(moves=moves, bot_color='w'))
                if bot_move.invalid_last_move:
                    resp_msg.set_text("Invalid move.")
                    return resp_msg
                elif bot_move.winner:
                    # endgame logic
                    resp_msg.set_images_pil([self.draw_endgame_board(bot_move['board_state'], bot_move['black_territory'], bot_move['white_territory'])])
                    winner = bot_move.winner
                    bcap = bot_move.black_captures
                    wcap = bot_move.white_captures
                    resp_msg.set_text(f"Winner: {winner}\nCaptures B: {bcap} - W: {wcap}")
                    board_state = {'moves': bot_move.moves }
                    resp_msg.set_extra_property(BOARD_STATE, board_state)
                    return resp_msg
                else:
                    board_state = {'moves': bot_move['moves'] }
                    board_img = self.draw_board(bot_move['board_state'], 
                                                last_move=self.parse_move(bot_move['moves'][-1][1]))
                    resp_msg.set_images_pil([board_img])
                    bcap = bot_move.black_captures
                    wcap = bot_move.white_captures]
                    resp_msg.set_text(f"Captures B: {bcap} - W: {wcap}")
                    resp_msg.set_extra_property(BOARD_STATE, board_state)
                    return resp_msg
            else :
                resp_msg.set_text("Invalid move. Move needs to be like this: D4")
        else:
            resp_msg.set_text("Can't find game state. Please start new game.")

        return resp_msg
    


