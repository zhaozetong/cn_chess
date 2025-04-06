import torch
import numpy as np
import random
import copy
from cn_chess import ChineseChess
from mcts.mcts import mcts_search

def evaluate_model(model, device, num_games=10, opponent='random', opponent_path=None):
    """评估模型性能
    
    参数:
        model: 要评估的模型
        device: 计算设备
        num_games: 评估局数
        opponent: 对手类型 ('random', 'past', 'self')
        opponent_path: 对手模型路径 (如果对手类型为'past')
    """
    wins = 0
    draws = 0
    losses = 0
    
    # 如果对手是过去的模型版本，加载它
    opponent_model = None
    if opponent == 'past' and opponent_path:
        from models.chess_net import ChessNet
        opponent_model = ChessNet()
        opponent_model.load_state_dict(torch.load(opponent_path, map_location=device))
        opponent_model.to(device)
        opponent_model.eval()
    elif opponent == 'self':
        opponent_model = copy.deepcopy(model)
    
    for game_idx in range(num_games):
        game = ChineseChess()
        current_player = 1  # 红方先手，被评估的模型总是红方
        
        while not game.is_game_over():
            if game.current_player == current_player:
                # 被评估的模型移动
                actions, action_probs, _ = mcts_search(game, model, device, num_simulations=50)
                best_action = actions[np.argmax(action_probs)]
            else:
                # 对手移动
                if opponent == 'random':
                    # 随机对手
                    legal_actions = game.get_legal_actions()
                    best_action = random.choice(legal_actions)
                else:
                    # 使用模型对手
                    actions, action_probs, _ = mcts_search(game, opponent_model, device, num_simulations=50)
                    best_action = actions[np.argmax(action_probs)]
            
            game.make_move(best_action[0], best_action[1])
        
        # 记录比赛结果
        winner = game.get_winner()
        if winner == current_player:
            wins += 1
            result = "胜利"
        elif winner is None:
            draws += 1
            result = "和棋"
        else:
            losses += 1
            result = "失败"
        
        print(f"评估游戏 {game_idx+1}/{num_games} - {result}")
    
    win_rate = wins / num_games
    print(f"评估结果: 胜率={win_rate:.2f}, 胜={wins}, 和={draws}, 负={losses}")
    return win_rate
