import numpy as np
import copy

class Piece:
    """棋子类,但是只是定义了棋子类型,没有棋子特性"""
    
    def __init__(self, piece_type, player, position):
        """
        初始化棋子
        :param piece_type: 棋子类型（车、马、相/象等）
        :param player: 所属玩家（1为红方，-1为黑方）
        :param position: 位置元组 (row, col)
        """
        self.piece_type = piece_type  # 1:车, 2:马, 3:相/象, 4:仕/士, 5:帅/将, 6:炮, 7:兵/卒
        self.player = player  # 1表示红方，-1表示黑方
        self.position = position  # (row, col)
        
    @property # 将方法转换为属性
    def id(self):
        """返回棋子的数字ID（与原始代码兼容）"""
        return self.piece_type * self.player
        
    def __str__(self):
        piece_names = {
            (1, 1): '车', (2, 1): '马', (3, 1): '相', (4, 1): '仕', 
            (5, 1): '帅', (6, 1): '炮', (7, 1): '兵',
            (1, -1): '車', (2, -1): '馬', (3, -1): '象', (4, -1): '士', 
            (5, -1): '將', (6, -1): '砲', (7, -1): '卒'
        }
        return piece_names.get((self.piece_type, self.player), ' ')

class ChineseChess:
    """中国象棋游戏类"""
    
    def __init__(self):
        """初始化棋盘和棋子"""
        # 棋盘大小: 10行 9列 (实际棋盘是9*10，但为了方便索引，使用10*9)
        self.board_size = (10, 9)
        
        # 初始化空棋盘
        self.board = np.zeros(self.board_size, dtype=np.int8)
        
        # 棋子字典，键为位置(row, col)，值为Piece对象
        self.pieces = {}
        
        # 红方棋子字典，键为棋子ID，值为Piece对象列表
        self.red_pieces = {}
        
        # 黑方棋子字典，键为棋子ID，值为Piece对象列表
        self.black_pieces = {}

        # 记录双方的将/帅位置，便于快速检查将军
        self.king_positions = {1: None, -1: None}
        # 初始化棋子
        self._init_pieces()
        
        # 当前玩家，1表示红方，-1表示黑方
        self.current_player = 1
        
        # 游戏是否结束
        self.game_over = False
        self.winner = None
        
        # 记录所有历史棋盘状态，用于检测重复局面
        self.history = [self.board.copy()]
        
        # 记录总步数和双方步数
        self.total_moves = 0
        self.red_moves = 0
        self.black_moves = 0
    
    def _init_pieces(self):
        """初始化棋盘上的所有棋子"""
        # 红方(下方)初始布局
        self._add_piece(1, 1, (9, 0))  # 车
        self._add_piece(1, 1, (9, 8))  # 车
        self._add_piece(2, 1, (9, 1))  # 马
        self._add_piece(2, 1, (9, 7))  # 马
        self._add_piece(3, 1, (9, 2))  # 相
        self._add_piece(3, 1, (9, 6))  # 相
        self._add_piece(4, 1, (9, 3))  # 仕
        self._add_piece(4, 1, (9, 5))  # 仕
        self._add_piece(5, 1, (9, 4))  # 帅
        self._add_piece(6, 1, (7, 1))  # 炮
        self._add_piece(6, 1, (7, 7))  # 炮
        self._add_piece(7, 1, (6, 0))  # 兵
        self._add_piece(7, 1, (6, 2))  # 兵
        self._add_piece(7, 1, (6, 4))  # 兵
        self._add_piece(7, 1, (6, 6))  # 兵
        self._add_piece(7, 1, (6, 8))  # 兵
        
        # 黑方(上方)初始布局
        self._add_piece(1, -1, (0, 0))  # 车
        self._add_piece(1, -1, (0, 8))  # 车
        self._add_piece(2, -1, (0, 1))  # 马
        self._add_piece(2, -1, (0, 7))  # 马
        self._add_piece(3, -1, (0, 2))  # 象
        self._add_piece(3, -1, (0, 6))  # 象
        self._add_piece(4, -1, (0, 3))  # 士
        self._add_piece(4, -1, (0, 5))  # 士
        self._add_piece(5, -1, (0, 4))  # 将
        self._add_piece(6, -1, (2, 1))  # 炮
        self._add_piece(6, -1, (2, 7))  # 炮
        self._add_piece(7, -1, (3, 0))  # 卒
        self._add_piece(7, -1, (3, 2))  # 卒
        self._add_piece(7, -1, (3, 4))  # 卒
        self._add_piece(7, -1, (3, 6))  # 卒
        self._add_piece(7, -1, (3, 8))  # 卒
    
    def _add_piece(self, piece_type, player, position):
        """添加棋子到棋盘"""
        row, col = position
        piece = Piece(piece_type, player, position)
        
        # 更新棋盘
        self.board[row, col] = piece.id
        
        # 更新棋子字典
        self.pieces[position] = piece
        
        # 更新玩家棋子字典
        player_pieces = self.red_pieces if player == 1 else self.black_pieces
        if piece_type not in player_pieces:
            player_pieces[piece_type] = []
        player_pieces[piece_type].append(piece)
        
        # 如果是将/帅，记录位置
        if piece_type == 5:
            self.king_positions[player] = position
    
    def get_piece_name(self, piece_id):
        """根据棋子ID获取名称"""
        if piece_id == 0:
            return ' '
        piece_names = {
            1: '车', 2: '马', 3: '相', 4: '仕', 5: '帅', 6: '炮', 7: '兵',
            -1: '車', -2: '馬', -3: '象', -4: '士', -5: '將', -6: '砲', -7: '卒'
        }
        return piece_names.get(piece_id, ' ')
    
    def display_board(self):
        """打印当前棋盘状态"""
        print('  ０１２３４５６７８')
        print(' ┌─┬─┬─┬─┬─┬─┬─┬─┐')
        
        for i in range(self.board_size[0]):
            print(f'{i}│', end='')
            for j in range(self.board_size[1]):
                print(f'{self.get_piece_name(self.board[i, j])}', end='')
                if j < self.board_size[1] - 1:
                    print('│', end='')
            print('│')
            
            if i < self.board_size[0] - 1:
                if i == 4:
                    # 河界
                    print(' ├─┼─┼─┼─┼─┼─┼─┼─┤')
                else:
                    print(' ├─┼─┼─┼─┼─┼─┼─┼─┤')
        
        print(' └─┴─┴─┴─┴─┴─┴─┴─┘')
        
        if self.current_player == 1:
            print("红方走棋")
        else:
            print("黑方走棋")
    
    def is_valid_position(self, pos):
        """检查位置是否在棋盘内"""
        row, col = pos
        return 0 <= row < self.board_size[0] and 0 <= col < self.board_size[1]
    
    def get_piece(self, pos):
        """获取指定位置的棋子，如果位置为空则返回None"""
        if pos in self.pieces:
            return self.pieces[pos]
        return None
    
    def get_piece_id(self, pos):
        """获取指定位置的棋子ID"""
        row, col = pos
        return self.board[row, col]
    
    def is_same_side(self, piece1_id, piece2_id):
        """判断两个棋子是否同边"""
        return piece1_id * piece2_id > 0  # 同符号表示同一方
    
    def get_valid_moves(self, pos):
        """获取指定位置棋子的所有合法移动"""
        piece = self.get_piece(pos)
        if not piece or piece.player != self.current_player:
            return []
        
        valid_moves = []
        
        # 根据不同类型的棋子计算合法移动
        if piece.piece_type == 1:  # 车
            valid_moves.extend(self._get_rook_moves(piece))
        elif piece.piece_type == 2:  # 马
            valid_moves.extend(self._get_knight_moves(piece))
        elif piece.piece_type == 3:  # 相/象
            valid_moves.extend(self._get_bishop_moves(piece))
        elif piece.piece_type == 4:  # 仕/士
            valid_moves.extend(self._get_advisor_moves(piece))
        elif piece.piece_type == 5:  # 帅/将
            valid_moves.extend(self._get_king_moves(piece))
        elif piece.piece_type == 6:  # 炮
            valid_moves.extend(self._get_cannon_moves(piece))
        elif piece.piece_type == 7:  # 兵/卒
            valid_moves.extend(self._get_pawn_moves(piece))
        
        return valid_moves
    
    def _get_rook_moves(self, piece):
        """获取车的合法移动"""
        row, col = piece.position
        moves = []
        
        # 四个方向: 上、右、下、左
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for d_row, d_col in directions:
            for step in range(1, max(self.board_size)):
                new_row, new_col = row + step*d_row, col + step*d_col
                new_pos = (new_row, new_col)
                
                # 超出边界
                if not self.is_valid_position(new_pos):
                    break
                
                target_id = self.board[new_row, new_col]
                
                # 空位
                if target_id == 0:
                    moves.append(new_pos)
                    continue
                
                # 敌方棋子，可以吃
                if not self.is_same_side(piece.id, target_id):
                    moves.append(new_pos)
                
                # 无论是友方还是敌方棋子，都不能继续前进
                break
        
        return moves
    
    def _get_knight_moves(self, piece):
        """获取马的合法移动"""
        row, col = piece.position
        moves = []
        
        # 马走"日"，先直后斜
        knight_moves = [
            (-2, -1), (-2, 1),  # 上两格，左或右一格
            (-1, -2), (-1, 2),  # 左两格，上或下一格
            (1, -2), (1, 2),    # 右两格，上或下一格
            (2, -1), (2, 1)     # 下两格，左或右一格
        ]
        
        # 马脚位置
        leg_positions = [
            (-1, 0), (-1, 0),   # 上两格的马脚
            (0, -1), (0, 1),    # 左两格的马脚
            (0, -1), (0, 1),    # 右两格的马脚
            (1, 0), (1, 0)      # 下两格的马脚
        ]
        
        for i, (d_row, d_col) in enumerate(knight_moves):
            new_row, new_col = row + d_row, col + d_col
            new_pos = (new_row, new_col)
            
            # 检查是否出界
            if not self.is_valid_position(new_pos):
                continue
            
            # 检查马脚是否被绊
            leg_row = row + leg_positions[i][0]
            leg_col = col + leg_positions[i][1]
            if self.board[leg_row, leg_col] != 0:
                continue
            
            target_id = self.board[new_row, new_col]
            
            # 目标位置为空或敌方棋子
            if target_id == 0 or not self.is_same_side(piece.id, target_id):
                moves.append(new_pos)
        
        return moves
    
    def _get_bishop_moves(self, piece):
        """获取相/象的合法移动"""
        row, col = piece.position
        moves = []
        
        # 相/象走田，四个方向
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        
        # 象眼位置
        eye_positions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for i, (d_row, d_col) in enumerate(directions):
            new_row, new_col = row + d_row, col + d_col
            new_pos = (new_row, new_col)
            
            # 检查是否出界或过河
            if not self.is_valid_position(new_pos):
                continue
                
            # 相不能过河
            if (piece.player > 0 and new_row < 5) or (piece.player < 0 and new_row > 4):
                continue
            
            # 检查象眼是否被塞
            eye_row = row + eye_positions[i][0]
            eye_col = col + eye_positions[i][1]
            if self.board[eye_row, eye_col] != 0:
                continue
            
            target_id = self.board[new_row, new_col]
            
            # 目标位置为空或敌方棋子
            if target_id == 0 or not self.is_same_side(piece.id, target_id):
                moves.append(new_pos)
        
        return moves
    
    def _get_advisor_moves(self, piece):
        """获取仕/士的合法移动"""
        row, col = piece.position
        moves = []
        
        # 仕/士走斜线
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            new_pos = (new_row, new_col)
            
            # 检查是否在九宫格内
            if not self.is_valid_position(new_pos):
                continue
            
            if piece.player > 0:  # 红方仕
                if not (7 <= new_row <= 9 and 3 <= new_col <= 5):
                    continue
            else:  # 黑方士
                if not (0 <= new_row <= 2 and 3 <= new_col <= 5):
                    continue
            
            target_id = self.board[new_row, new_col]
            
            # 目标位置为空或敌方棋子
            if target_id == 0 or not self.is_same_side(piece.id, target_id):
                moves.append(new_pos)
        
        return moves
    
    def _get_king_moves(self, piece):
        """获取帅/将的合法移动"""
        row, col = piece.position
        moves = []
        
        # 帅/将走一格（上下左右）
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for d_row, d_col in directions:
            new_row, new_col = row + d_row, col + d_col
            new_pos = (new_row, new_col)
            
            # 检查是否在九宫格内
            if not self.is_valid_position(new_pos):
                continue
            
            if piece.player > 0:  # 红方帅
                if not (7 <= new_row <= 9 and 3 <= new_col <= 5):
                    continue
            else:  # 黑方将
                if not (0 <= new_row <= 2 and 3 <= new_col <= 5):
                    continue
            
            target_id = self.board[new_row, new_col]
            
            # 目标位置为空或敌方棋子
            if target_id == 0 or not self.is_same_side(piece.id, target_id):
                moves.append(new_pos)
        
        # 将帅对面特殊情况 - 允许直接吃对方的将/帅
        opponent_king_pos = self.king_positions[-piece.player]
        if opponent_king_pos and opponent_king_pos[1] == col:  # 同一列
            # 检查两个将/帅之间是否有棋子
            min_row = min(row, opponent_king_pos[0])
            max_row = max(row, opponent_king_pos[0])
            has_piece_between = False
            
            for r in range(min_row + 1, max_row):
                if self.board[r, col] != 0:
                    has_piece_between = True
                    break
            
            if not has_piece_between:
                moves.append(opponent_king_pos)
        
        return moves
    
    def _get_cannon_moves(self, piece):
        """获取炮的合法移动"""
        row, col = piece.position
        moves = []
        
        # 四个方向: 上、右、下、左
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for d_row, d_col in directions:
            has_platform = False
            
            for step in range(1, max(self.board_size)):
                new_row, new_col = row + step*d_row, col + step*d_col
                new_pos = (new_row, new_col)
                
                # 超出边界
                if not self.is_valid_position(new_pos):
                    break
                
                target_id = self.board[new_row, new_col]
                
                if not has_platform:
                    # 未翻山，行走规则与车相同
                    if target_id == 0:
                        moves.append(new_pos)
                        continue
                    else:
                        # 找到炮架
                        has_platform = True
                        continue
                else:
                    # 已经翻山，可以吃子
                    if target_id == 0:
                        continue
                    elif not self.is_same_side(piece.id, target_id):
                        moves.append(new_pos)
                    
                    # 无论是否可以吃子，找到棋子后停止
                    break
        
        return moves
    
    def _get_pawn_moves(self, piece):
        """获取兵/卒的合法移动"""
        row, col = piece.position
        moves = []
        
        if piece.player > 0:  # 红方兵
            # 未过河，只能前进
            if row > 4:
                if row - 1 >= 0:
                    target_id = self.board[row-1, col]
                    if target_id == 0 or target_id < 0:  # 空位或敌方棋子
                        moves.append((row-1, col))
            else:
                # 过河后，可以左右移动
                directions = [(-1, 0), (0, -1), (0, 1)]  # 上、左、右
                for d_row, d_col in directions:
                    new_row, new_col = row + d_row, col + d_col
                    if self.is_valid_position((new_row, new_col)):
                        target_id = self.board[new_row, new_col]
                        if target_id == 0 or target_id < 0:  # 空位或敌方棋子
                            moves.append((new_row, new_col))
        else:  # 黑方卒
            # 未过河，只能前进
            if row < 5:
                if row + 1 < self.board_size[0]:
                    target_id = self.board[row+1, col]
                    if target_id == 0 or target_id > 0:  # 空位或敌方棋子
                        moves.append((row+1, col))
            else:
                # 过河后，可以左右移动
                directions = [(1, 0), (0, -1), (0, 1)]  # 下、左、右
                for d_row, d_col in directions:
                    new_row, new_col = row + d_row, col + d_col
                    if self.is_valid_position((new_row, new_col)):
                        target_id = self.board[new_row, new_col]
                        if target_id == 0 or target_id > 0:  # 空位或敌方棋子
                            moves.append((new_row, new_col))
        
        return moves
    
    def make_move(self, from_pos, to_pos):
        """移动棋子并更新游戏状态"""
        # 检查移动是否合法
        valid_moves = self.get_valid_moves(from_pos)
        if to_pos not in valid_moves:
            return False
        
        # 获取移动的棋子
        piece = self.get_piece(from_pos)
        if not piece:
            return False
        
        # 保存移动前的状态，便于执行完后恢复
        to_row, to_col = to_pos
        captured_id = self.board[to_row, to_col]
        captured_piece = self.get_piece(to_pos)
        
        # 更新棋盘和棋子位置
        from_row, from_col = from_pos
        self.board[to_row, to_col] = piece.id
        self.board[from_row, from_col] = 0
        
        # 更新棋子字典
        self.pieces.pop(from_pos, None)
        if captured_piece:
            # 如果吃子，从对应的棋子列表中移除
            player_pieces = self.black_pieces if captured_piece.player == -1 else self.red_pieces
            if captured_piece.piece_type in player_pieces:
                player_pieces[captured_piece.piece_type].remove(captured_piece)
            if abs(captured_id) == 5:
                # 如果吃掉的是将/帅，更新其位置
                self.king_positions[-captured_piece.player] = None
        
        # 更新棋子位置信息
        piece.position = to_pos
        self.pieces[to_pos] = piece
        
        # 如果移动的是将/帅，更新其位置信息
        if piece.piece_type == 5:
            self.king_positions[piece.player] = to_pos
        
        # 检查移动后是否被将军
        if self._is_checked(self.current_player):
            # 移动导致被将军，撤销移动
            self.board[from_row, from_col] = piece.id
            self.board[to_row, to_col] = captured_id
            piece.position = from_pos
            self.pieces[from_pos] = piece
            self.pieces.pop(to_pos, None)
            
            # 恢复被吃的棋子
            if captured_piece:
                self.pieces[to_pos] = captured_piece
                player_pieces = self.black_pieces if captured_piece.player == -1 else self.red_pieces
                if captured_piece.piece_type in player_pieces:
                    player_pieces[captured_piece.piece_type].append(captured_piece)
            
            # 恢复将/帅位置
            if piece.piece_type == 5:
                self.king_positions[piece.player] = from_pos
            
            return False
        
        # 更新步数
        self.total_moves += 1
        if self.current_player == 1:
            self.red_moves += 1
        else:
            self.black_moves += 1
        
        # 交换玩家
        self.current_player *= -1
        
        # 检查对方是否被将死（新的当前玩家）
        if self._check_game_over(self.current_player):
            self.game_over = True
            self.winner = -self.current_player  # 上一个玩家获胜
        
        # 记录当前局面
        self.history.append(self.board.copy())
        
        return True
    
    def _is_checked(self, player):
        """检查指定玩家是否被将军"""
        king_pos = self.king_positions[player]
        if not king_pos:
            return False
        
        # 获取对方所有棋子
        opponent_pieces = self.black_pieces if player == 1 else self.red_pieces
        
        # 检查对方每种类型的棋子
        for piece_type, pieces in opponent_pieces.items():
            for piece in pieces:
                moves = []
                if piece_type == 1:  # 车
                    moves = self._get_rook_moves(piece)
                elif piece_type == 2:  # 马
                    moves = self._get_knight_moves(piece)
                elif piece_type == 3:  # 相/象
                    moves = self._get_bishop_moves(piece)
                elif piece_type == 4:  # 仕/士
                    moves = self._get_advisor_moves(piece)
                elif piece_type == 5:  # 帅/将
                    moves = self._get_king_moves(piece)
                elif piece_type == 6:  # 炮
                    moves = self._get_cannon_moves(piece)
                elif piece_type == 7:  # 兵/卒
                    moves = self._get_pawn_moves(piece)
                
                if king_pos in moves:
                    return True
        
        return False
    
    def _check_game_over(self, player):
        """检查指定玩家是否被将死或无子可动"""
        # 首先检查对方的将/帅是否还存在
        opponent_king_exists = self.king_positions[-player] is not None
        
        # 如果对方的将/帅不存在，游戏结束
        if not opponent_king_exists:
            self.winner = player  # 当前玩家获胜
            return True
        
        # 检查玩家是否被将军
        if not self._is_checked(player):
            return False  # 没有被将军，游戏未结束
        
        # 检查是否有任何合法移动可以解除将军
        return self._no_valid_moves(player)
    
    def _no_valid_moves(self, player):
        """检查指定玩家是否无子可动"""
        player_pieces = self.red_pieces if player == 1 else self.black_pieces
        
        for piece_type, pieces in player_pieces.items():
            for piece in pieces:
                from_pos = piece.position
                valid_moves = self.get_valid_moves(from_pos)
                
                for to_pos in valid_moves:
                    # 尝试移动
                    to_row, to_col = to_pos
                    from_row, from_col = from_pos
                    
                    # 保存当前状态
                    captured_id = self.board[to_row, to_col]
                    captured_piece = self.get_piece(to_pos)
                    
                    # 模拟移动
                    self.board[to_row, to_col] = piece.id
                    self.board[from_row, from_col] = 0
                    
                    # 暂时更新棋子位置
                    old_pos = piece.position
                    piece.position = to_pos
                    self.pieces.pop(from_pos, None)
                    self.pieces[to_pos] = piece
                    
                    # 如果是将/帅，更新位置信息
                    old_king_pos = None
                    if piece.piece_type == 5:
                        old_king_pos = self.king_positions[player]
                        self.king_positions[player] = to_pos
                    
                    # 检查移动后是否仍被将军
                    still_checked = self._is_checked(player)
                    
                    # 恢复棋盘和棋子位置
                    self.board[from_row, from_col] = piece.id
                    self.board[to_row, to_col] = captured_id
                    piece.position = old_pos
                    self.pieces[from_pos] = piece
                    self.pieces.pop(to_pos, None)
                    
                    # 恢复被吃的棋子
                    if captured_piece:
                        self.pieces[to_pos] = captured_piece
                    
                    # 恢复将/帅位置
                    if old_king_pos:
                        self.king_positions[player] = old_king_pos
                    
                    if not still_checked:
                        return False  # 找到一个有效移动，可以解除将军
        
        return True  # 无有效移动可以解除将军
    
    def get_state(self):
        """返回游戏状态，用于AI训练"""
        # 将棋盘状态转换为适合神经网络的表示形式
        # 可以为每种棋子类型创建一个平面
        planes = []
        
        # 为每种棋子类型创建一个平面
        for piece_type in range(-7, 8):
            if piece_type == 0:
                continue
            
            plane = np.zeros(self.board_size, dtype=np.float32)
            for i in range(self.board_size[0]):
                for j in range(self.board_size[1]):
                    if self.board[i, j] == piece_type:
                        plane[i, j] = 1
            
            planes.append(plane)
        
        # 添加当前玩家的平面
        player_plane = np.ones(self.board_size, dtype=np.float32) * (self.current_player == 1)
        planes.append(player_plane)
        
        return np.stack(planes)
    
    def get_legal_actions(self):
        """返回当前玩家的所有合法动作"""
        actions = []
        player_pieces = self.red_pieces if self.current_player == 1 else self.black_pieces
        
        for piece_type, pieces in player_pieces.items():
            for piece in pieces:
                from_pos = piece.position
                for to_pos in self.get_valid_moves(from_pos):
                    # 确保移动后不会被将军
                    from_row, from_col = from_pos
                    to_row, to_col = to_pos
                    
                    # 保存当前状态
                    captured_id = self.board[to_row, to_col]
                    captured_piece = self.get_piece(to_pos)
                    
                    # 模拟移动
                    self.board[to_row, to_col] = piece.id
                    self.board[from_row, from_col] = 0
                    
                    # 暂时更新棋子位置
                    old_pos = piece.position
                    piece.position = to_pos
                    self.pieces.pop(from_pos, None)
                    self.pieces[to_pos] = piece
                    
                    # 如果是将/帅，更新位置信息
                    old_king_pos = None
                    if piece.piece_type == 5:
                        old_king_pos = self.king_positions[self.current_player]
                        self.king_positions[self.current_player] = to_pos
                    
                    # 检查移动后是否被将军
                    checked = self._is_checked(self.current_player)
                    
                    # 恢复棋盘和棋子位置
                    self.board[from_row, from_col] = piece.id
                    self.board[to_row, to_col] = captured_id
                    piece.position = old_pos
                    self.pieces[from_pos] = piece
                    self.pieces.pop(to_pos, None)
                    
                    # 恢复被吃的棋子
                    if captured_piece:
                        self.pieces[to_pos] = captured_piece
                    
                    # 恢复将/帅位置
                    if old_king_pos:
                        self.king_positions[self.current_player] = old_king_pos
                    
                    if not checked:
                        actions.append((from_pos, to_pos))
        
        return actions
    
    def evaluate(self):
        """评估当前局面"""
        # 棋子价值
        piece_values = {
            1: 9, 2: 4, 3: 2, 4: 2, 5: 100, 6: 4.5, 7: 1
        }
        
        score = 0
        
        # 计算红方分数
        for piece_type, pieces in self.red_pieces.items():
            score += len(pieces) * piece_values.get(piece_type, 0)
        
        # 计算黑方分数
        for piece_type, pieces in self.black_pieces.items():
            score -= len(pieces) * piece_values.get(piece_type, 0)
        
        return score * self.current_player  # 从当前玩家角度评估
    
    def is_game_over(self):
        """检查游戏是否结束"""
        return self.game_over
    
    def get_winner(self):
        """获取赢家，1表示红方，-1表示黑方，0表示平局，None表示未结束"""
        return self.winner
    
    def clone(self):
        """深拷贝游戏状态"""
        new_game = ChineseChess.__new__(ChineseChess)
        new_game.board_size = self.board_size
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.history = [board.copy() for board in self.history]
        new_game.total_moves = self.total_moves
        new_game.red_moves = self.red_moves
        new_game.black_moves = self.black_moves
        
        # 复制棋子信息
        new_game.pieces = {}
        new_game.red_pieces = {}
        new_game.black_pieces = {}
        new_game.king_positions = {1: self.king_positions[1], -1: self.king_positions[-1]}
        
        for pos, piece in self.pieces.items():
            new_piece = Piece(piece.piece_type, piece.player, piece.position)
            new_game.pieces[pos] = new_piece
            
            player_pieces = new_game.red_pieces if piece.player == 1 else new_game.black_pieces
            if piece.piece_type not in player_pieces:
                player_pieces[piece.piece_type] = []
            player_pieces[piece.piece_type].append(new_piece)
        
        return new_game

# 游戏测试代码
def play_human_vs_human():
    game = ChineseChess()
    
    while not game.is_game_over():
        game.display_board()
        
        try:
            from_pos = input("输入起始位置 (行,列): ")
            if from_pos.lower() == 'q':
                print("游戏结束")
                break
                
            from_row, from_col = map(int, from_pos.split(','))
            
            # 显示可能的移动
            valid_moves = game.get_valid_moves((from_row, from_col))
            print(f"可能的移动: {valid_moves}")
            
            to_pos = input("输入目标位置 (行,列): ")
            if to_pos.lower() == 'q':
                print("游戏结束")
                break
                
            to_row, to_col = map(int, to_pos.split(','))
            
            if game.make_move((from_row, from_col), (to_row, to_col)):
                print("移动成功")
            else:
                print("非法移动，请重试")
        except Exception as e:
            print(f"输入错误: {e}")
    
    if game.is_game_over():
        game.display_board()
        winner = game.get_winner()
        if winner == 1:
            print("红方胜利!")
        elif winner == -1:
            print("黑方胜利!")
        else:
            print("平局!")

if __name__ == "__main__":
    play_human_vs_human()
