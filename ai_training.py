import torch
import torch.optim as optim
import numpy as np
import random
import os
import argparse
from models.chess_net import ChessNet
from memory.replay_buffer import ReplayBuffer
from mcts.mcts import mcts_search
from training.self_play import self_play
from training.trainer import train_network
from evaluation.evaluator import evaluate_model

def main(args):
    """主训练流程"""
    # 创建保存模型的目录
    os.makedirs(args.save_dir, exist_ok=True)
    
    # 检查是否使用CUDA
    device = torch.device("cuda" if torch.cuda.is_available() and args.use_cuda else "cpu")
    print(f"使用设备: {device}")
    
    # 初始化模型
    model = ChessNet(args.input_channels)
    model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    replay_buffer = ReplayBuffer(capacity=args.buffer_capacity)
    
    # 加载已有模型（如果存在）
    if args.load_model and os.path.exists(args.load_model):
        model.load_state_dict(torch.load(args.load_model, map_location=device))
        print(f"已加载模型: {args.load_model}")
    
    best_win_rate = 0.0
    current_opponent = None  # 初始对手为随机
    
    # 训练第一阶段：对抗随机策略
    if args.train_against_random:
        print("阶段1: 训练对抗随机策略")
        for iteration in range(args.random_iterations):
            print(f"随机对弈迭代 {iteration+1}/{args.random_iterations}")
            
            # 对抗随机收集数据
            training_data = self_play(model, device, num_games=args.games_per_iteration, 
                                     mcts_simulations=args.mcts_simulations, 
                                     opponent='random')
            
            # 存入回放缓冲区
            for data in training_data:
                replay_buffer.add(*data)
            
            # 训练网络
            if len(replay_buffer) >= args.batch_size:
                batch = replay_buffer.sample(args.batch_size)
                train_network(model, optimizer, batch, device, epochs=args.epochs, batch_size=args.batch_size)
            
            # 评估并保存模型
            win_rate = evaluate_model(model, device, num_games=args.eval_games, opponent='random')
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                torch.save(model.state_dict(), os.path.join(args.save_dir, "model_vs_random_best.pth"))
                print(f"保存新的最佳模型, 胜率: {best_win_rate:.2f}")
            
            torch.save(model.state_dict(), os.path.join(args.save_dir, f"model_vs_random_{iteration}.pth"))
            print(f"完成随机对弈迭代 {iteration+1}/{args.random_iterations}, 当前胜率: {win_rate:.2f}")
        
        # 第一阶段结束后保存模型作为基础模型
        base_model_path = os.path.join(args.save_dir, "base_model.pth")
        torch.save(model.state_dict(), base_model_path)
        print(f"基础模型已保存: {base_model_path}")
        current_opponent = 'self'  # 更新对手为自我博弈
    
    # 训练第二阶段：自我博弈
    print("阶段2: 自我博弈训练")
    best_win_rate = 0.0  # 重置最佳胜率
    
    for iteration in range(args.self_play_iterations):
        print(f"自我博弈迭代 {iteration+1}/{args.self_play_iterations}")
        
        # 自我对弈收集数据
        training_data = self_play(model, device, num_games=args.games_per_iteration, 
                                 mcts_simulations=args.mcts_simulations, 
                                 opponent='self')
        
        # 存入回放缓冲区
        for data in training_data:
            replay_buffer.add(*data)
        
        # 从缓冲区采样训练
        if len(replay_buffer) >= args.batch_size:
            batch = replay_buffer.sample(args.batch_size)
            train_network(model, optimizer, batch, device, epochs=args.epochs, batch_size=args.batch_size)
        
        # 评估模型（对抗较早版本）
        if iteration % args.eval_frequency == 0:
            # 每隔几次迭代加载较早版本进行对抗评估
            if iteration >= args.eval_against_past and os.path.exists(os.path.join(args.save_dir, f"model_iter_{iteration-args.eval_against_past}.pth")):
                win_rate = evaluate_model(model, device, num_games=args.eval_games, 
                                         opponent='past', 
                                         opponent_path=os.path.join(args.save_dir, f"model_iter_{iteration-args.eval_against_past}.pth"))
                print(f"对抗历史模型评估: 胜率={win_rate:.2f}")
            else:
                win_rate = evaluate_model(model, device, num_games=args.eval_games, opponent='random')
                print(f"对抗随机模型评估: 胜率={win_rate:.2f}")
            
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                torch.save(model.state_dict(), os.path.join(args.save_dir, "model_best.pth"))
                print(f"保存新的最佳模型, 胜率: {best_win_rate:.2f}")
        
        # 保存模型检查点
        torch.save(model.state_dict(), os.path.join(args.save_dir, f"model_iter_{iteration}.pth"))
        print(f"完成自我博弈迭代 {iteration+1}/{args.self_play_iterations}")
    
    # 保存最终模型
    torch.save(model.state_dict(), os.path.join(args.save_dir, "model_final.pth"))
    print("训练完成！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="中国象棋AI训练程序")
    
    # 模型参数
    parser.add_argument("--input_channels", type=int, default=15, help="输入通道数")
    
    # 训练参数
    parser.add_argument("--learning_rate", type=float, default=0.001, help="学习率")
    parser.add_argument("--buffer_capacity", type=int, default=10000, help="回放缓冲区容量")
    parser.add_argument("--batch_size", type=int, default=128, help="批次大小")
    parser.add_argument("--epochs", type=int, default=10, help="每次迭代的训练轮数")
    parser.add_argument("--mcts_simulations", type=int, default=50, help="MCTS模拟次数")
    parser.add_argument("--save_dir", type=str, default="models/saved", help="模型保存目录")
    parser.add_argument("--use_cuda", action="store_true", help="是否使用CUDA")
    parser.add_argument("--load_model", type=str, default=None, help="加载预训练模型路径")
    
    # 对抗随机策略参数
    parser.add_argument("--train_against_random", action="store_true", help="是否先对抗随机策略训练")
    parser.add_argument("--random_iterations", type=int, default=10, help="对抗随机策略的迭代次数")
    
    # 自我博弈参数
    parser.add_argument("--self_play_iterations", type=int, default=50, help="自我博弈的迭代次数")
    parser.add_argument("--games_per_iteration", type=int, default=10, help="每次迭代的对弈局数")
    
    # 评估参数
    parser.add_argument("--eval_games", type=int, default=10, help="评估时的对弈局数")
    parser.add_argument("--eval_frequency", type=int, default=5, help="评估频率（迭代次数）")
    parser.add_argument("--eval_against_past", type=int, default=10, help="对抗多少迭代之前的模型")
    
    args = parser.parse_args()
    main(args)
