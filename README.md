# 象棋机器人
### 文件结构:
* cn_chess.py 基座
* game.py 可视化游戏

#### 训练
```powershell
# 先训练对抗随机策略，然后自我博弈，使用CUDA加速
python ai_training.py --use_cuda --train_against_random

# 加载已有模型继续训练
python ai_training.py --use_cuda --load_model models/saved/model_best.pth

# 只进行自我博弈（跳过随机对弈阶段）
python ai_training.py --use_cuda

# 自定义参数
python ai_training.py --use_cuda --self_play_iterations 100 --mcts_simulations 200 --batch_size 256
```
