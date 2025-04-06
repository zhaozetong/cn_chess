import torch
import torch.nn as nn

class ChessNet(nn.Module):
    """中国象棋神经网络模型"""
    def __init__(self, input_channels=15):
        super(ChessNet, self).__init__()
        # 输入通道数：7种红棋 + 7种黑棋 + 当前玩家
        self.input_channels = input_channels
        
        # 共享特征提取层
        self.common_layers = nn.Sequential(
            nn.Conv2d(self.input_channels, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU()
        )
        
        # 策略头 - 输出动作概率
        # 中国象棋最大可能的动作数为：约90个棋子位置 * 90个目标位置 = 8100
        # 但实际上可能的移动远少于此，我们使用(10*9)*(10*9)=8100作为上限
        self.policy_head = nn.Sequential(
            nn.Conv2d(128, 32, kernel_size=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(32 * 10 * 9, 2086)  # 更准确的动作空间大小估计
        )
        
        # 价值头 - 估计当前局面价值
        self.value_head = nn.Sequential(
            nn.Conv2d(128, 1, kernel_size=1),
            nn.BatchNorm2d(1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(10 * 9, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh()  # 输出范围(-1, 1)
        )
    
    def forward(self, x):
        """前向传播"""
        common_features = self.common_layers(x)
        policy_logits = self.policy_head(common_features)
        value = self.value_head(common_features)
        return policy_logits, value
