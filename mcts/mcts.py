import torch
import numpy as np
from .mcts_node import MCTSNode

def mcts_search(game, model, device, num_simulations=100, temperature=1.0):
    """执行蒙特卡洛树搜索"""
    root = MCTSNode(game)
    
    for _ in range(num_simulations):
        node = root
        search_path = [node]
        
        # 选择阶段 - 遍历到叶节点
        while node.is_expanded and node.children:
            move, node = node.select_child()
            search_path.append(node)
        
        # 如果游戏已结束，使用真实的结果
        if node.game.is_game_over():
            value = node.game.get_winner()
            if value is None:
                value = 0  # 和棋
        else:
            # 扩展阶段 - 如果节点未扩展，使用神经网络评估
            state = node.game.get_state()
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
            
            with torch.no_grad():
                policy_logits, value_tensor = model(state_tensor)
                policy = torch.softmax(policy_logits, dim=1).squeeze(0).cpu().numpy()
                value = value_tensor.item()
            
            # 扩展节点
            node.expand(policy)
        
        # 反向传播阶段 - 更新路径上所有节点的统计信息
        for node in reversed(search_path):
            # 根据当前玩家调整价值
            node_value = value if node.game.current_player == game.current_player else -value
            node.update(node_value)
    
    # 根据访问次数计算移动概率
    visit_counts = np.array([child.visits for child in root.children.values()])
    actions = list(root.children.keys())
    
    if temperature == 0:  # 确定性选择
        best_idx = np.argmax(visit_counts)
        action_probs = np.zeros_like(visit_counts, dtype=np.float32)
        action_probs[best_idx] = 1.0
    else:  # 随机选择，温度越高随机性越大
        # 应用温度参数
        visit_count_distribution = visit_counts ** (1.0 / temperature)
        # 归一化
        action_probs = visit_count_distribution / np.sum(visit_count_distribution)
    
    # 构建完整的策略向量
    full_policy = np.zeros(2086)  # 与策略头输出维度匹配
    for action, prob in zip(actions, action_probs):
        idx = root.move_to_index(action)
        if idx < len(full_policy):
            full_policy[idx] = prob
    
    return actions, action_probs, full_policy
