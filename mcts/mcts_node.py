import numpy as np

class MCTSNode:
    """蒙特卡洛树搜索节点"""
    def __init__(self, game, parent=None, move=None, prior=0):
        self.game = game
        self.parent = parent
        self.move = move  # 从父节点到此节点的移动，格式为(from_pos, to_pos)
        self.children = {}  # 子节点，键为移动，值为节点
        
        self.visits = 0  # 访问次数
        self.value_sum = 0.0  # 累计价值
        self.prior = prior  # 先验概率
        
        self.is_expanded = False
    
    def select_child(self, c_puct=1.0):
        """使用PUCT公式选择最佳子节点"""
        best_score = -float('inf')
        best_move = None
        
        for move, child in self.children.items():
            # PUCT公式 = Q(s,a) + c_puct * P(s,a) * √∑_b N(s,b) / (1 + N(s,a))
            if child.visits > 0:
                q_value = child.value_sum / child.visits
            else:
                q_value = 0
                
            # 计算UCB分数
            exploration = c_puct * child.prior * (np.sqrt(self.visits) / (1 + child.visits))
            score = q_value + exploration
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move, self.children[best_move]
    
    def expand(self, policy):
        """扩展节点，添加所有可能的子节点"""
        legal_actions = self.game.get_legal_actions()
        
        # 为每个合法移动创建子节点
        for move in legal_actions:
            if move not in self.children:
                # 创建新游戏状态
                next_game = self.game.clone()
                next_game.make_move(move[0], move[1])
                
                # 获取此移动的先验概率（从策略网络）
                move_idx = self.move_to_index(move)
                prior = policy[move_idx] if move_idx < len(policy) else 0.001
                
                # 创建子节点
                self.children[move] = MCTSNode(next_game, parent=self, move=move, prior=prior)
        
        self.is_expanded = True
    
    @staticmethod
    def move_to_index(move):
        """将移动转换为策略向量的索引"""
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        # 将移动映射到一维索引
        board_size = 10 * 9
        return from_row * 9 + from_col + (to_row * 9 + to_col) * board_size
    
    def update(self, value):
        """更新节点统计信息"""
        self.visits += 1
        self.value_sum += value
    
    def get_value(self):
        """获取节点的平均价值"""
        if self.visits == 0:
            return 0
        return self.value_sum / self.visits
