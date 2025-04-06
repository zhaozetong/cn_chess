import torch
import numpy as np
import random
import copy
from cn_chess import ChineseChess
from mcts.mcts import mcts_search
from mcts.mcts_node import MCTSNode  # 添加MCTSNode的导入

def self_play(model, device, num_games=10, mcts_simulations=100, opponent='self', opponent_model=None):
    """自我对弈或与其他对手对弈收集训练数据
    
    参数:
        model: 主模型
        device: 计算设备
        num_games: 对弈局数
        mcts_simulations: MCTS模拟次数
        opponent: 对手类型 ('self', 'random', 'model')
        opponent_model: 对手模型 (如果对手类型为'model')
    """
    training_data = []
    
    for game_idx in range(num_games):
        game = ChineseChess()
        game_memory = []
        
        # 如果对手是自己，使用相同模型
        if opponent == 'self':
            opponent_model = model
        
        while not game.is_game_over():
            state = game.get_state()
            
            # 确定当前移动的模型
            if game.current_player == 1 or opponent == 'self':
                current_model = model
            elif opponent == 'model' and opponent_model is not None:
                current_model = opponent_model
            else:  # 随机对手
                # 随机移动
                legal_actions = game.get_legal_actions()
                action = random.choice(legal_actions)
                # 构建一个全零策略，只在选择的动作处为1
                full_policy = np.zeros(2086)
                idx = MCTSNode.move_to_index(action)
                if idx < len(full_policy):
                    full_policy[idx] = 1.0
                
                # 记录状态和策略
                game_memory.append((state, full_policy, None))
                
                # 执行动作
                game.make_move(action[0], action[1])
                continue
            
            # 使用MCTS搜索最佳动作
            actions, action_probs, full_policy = mcts_search(game, current_model, device, num_simulations=mcts_simulations)
            
            # 根据概率选择动作
            action_idx = np.random.choice(len(actions), p=action_probs)
            action = actions[action_idx]
            
            # 记录当前状态和动作概率
            game_memory.append((state, full_policy, None))
            
            # 执行动作
            game.make_move(action[0], action[1])
        
        # 游戏结束，填充价值标签
        winner = game.get_winner()
        value = 0
        if winner == 1:  # 红方胜
            value = 1
        elif winner == -1:  # 黑方胜
            value = -1
        
        # 更新所有游戏状态的价值
        for i in range(len(game_memory)):
            state, policy_vector, _ = game_memory[i]
            # 根据当前玩家调整价值
            player = 1 if i % 2 == 0 else -1
            adjusted_value = value * player
            # 添加到训练数据
            training_data.append((state, policy_vector, adjusted_value))
        
        print(f"游戏 {game_idx+1}/{num_games} 完成, 胜者: {'红方' if winner == 1 else '黑方' if winner == -1 else '和棋'}")
    
    return training_data
