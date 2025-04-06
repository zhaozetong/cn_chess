# 中国象棋游戏接口文档

## 导入方式
```python
from cn_chess import ChineseChess, Piece
```

## 主要类

### 1. Piece 类
棋子类，表示棋盘上的一个棋子。


#### 源码
```python

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
```

#### 属性:
- piece_type: 棋子类型（1:车, 2:马, 3:相/象, 4:仕/士, 5:帅/将, 6:炮, 7:兵/卒）
- player: 所属玩家（1为红方，-1为黑方）
- position: 位置元组 (row, col)
- id: 棋子的数字ID（piece_type * player）

### 2. ChineseChess 类
中国象棋游戏类，管理棋盘状态和游戏规则。

#### 属性构建源码:
``` python
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

```


#### 初始化:
```python
game = ChineseChess()  # 创建一个新的象棋游戏实例
```

#### 主要属性:
- board: 10x9的numpy数组，表示棋盘状态，0表示空位置，其他数字表示棋子ID
- pieces: 字典，键为位置(row, col)，值为Piece对象
- red_pieces/black_pieces: 双方棋子字典，键为棋子类型，值为Piece对象列表
- current_player: 当前玩家，1表示红方，-1表示黑方
- game_over: 布尔值，游戏是否结束
- winner: 赢家，1表示红方，-1表示黑方，None表示未结束
- history: 记录了一局从开始到当前局面,元素为棋子(如-2,0,3等),以np.array()格式,dtype=int8

## 主要方法

### 显示和状态方法

#### display_board()
打印当前棋盘状态到控制台。
```python
game.display_board()
```

#### get_state()
返回适合神经网络训练的游戏状态表示。
```python
state = game.get_state()  # 返回每种棋子类型的平面堆叠，最后一个平面表示当前玩家
```

#### is_game_over()
检查游戏是否结束。
```python
if game.is_game_over():
    print("游戏结束")
```

#### get_winner()
获取游戏赢家。
```python
winner = game.get_winner()  # 1表示红方，-1表示黑方，None表示未结束
```

#### evaluate()
评估当前局面，从当前玩家角度返回分数,但是这里的实现非常简单(给每个棋子一个分数然后直接相加)
建议使用训练出来的网络等结果去得到一个更加合理的分数
```python
score = game.evaluate()  # 正值对当前玩家有利，负值不利
```

### 移动和规则方法

#### get_valid_moves(position)
获取指定位置棋子的所有合法移动。
```python
moves = game.get_valid_moves((row, col))  # 返回可能移动的位置列表
```

#### get_legal_actions()
获取当前玩家的所有合法动作。
```python
actions = game.get_legal_actions()  # 返回(from_pos, to_pos)元组的列表
```

#### make_move(from_pos, to_pos)
尝试移动棋子并更新游戏状态。
如果移动导致被将军，会自动撤销移动并返回False。
```python
success = game.make_move((from_row, from_col), (to_row, to_col))
# 如果移动成功，返回True，并且更新游戏状态（交换当前玩家等）
# 如果移动不合法或导致被将军，返回False，棋盘状态不变
```

### 辅助方法

#### clone()
创建游戏当前状态的深拷贝。
```python
new_game = game.clone()  # 用于模拟移动而不影响原游戏状态
```

## 特别注意事项

1. **移动撤销机制**: 当一个移动会导致本方被将军时，`make_move()`会自动撤销这个移动并返回False。这在实现AI时非常重要，因为不需要额外检查移动是否导致被将军。

2. **合法动作生成**: `get_legal_actions()`已经过滤掉了会导致被将军的动作，可直接用于AI训练。

3. **游戏结束条件**: 当一方被将死或无子可动时，游戏结束。可以通过`is_game_over()`和`get_winner()`检查。

4. **游戏状态表示**: `get_state()`提供了适合神经网络的状态表示，包含了每种棋子的位置和当前玩家信息。

## 使用示例

### 简单人类对弈
```python
game = ChineseChess()

while not game.is_game_over():
    game.display_board()
    
    # 获取玩家输入
    from_row, from_col = map(int, input("输入起始位置 (行,列): ").split(','))
    to_row, to_col = map(int, input("输入目标位置 (行,列): ").split(','))
    
    # 尝试移动
    if game.make_move((from_row, from_col), (to_row, to_col)):
        print("移动成功")
    else:
        print("非法移动")

# 游戏结束
winner = game.get_winner()
if winner == 1:
    print("红方胜利!")
elif winner == -1:
    print("黑方胜利!")
```

### AI训练示例
```python
game = ChineseChess()
while not game.is_game_over():
    # 获取当前状态
    state = game.get_state()
    
    # 获取所有合法动作
    legal_actions = game.get_legal_actions()
    
    # AI选择一个动作 (例如使用策略网络)
    from_pos, to_pos = select_action(state, legal_actions)
    
    # 执行动作
    game.make_move(from_pos, to_pos)
    
    # 计算奖励等...
```
