import torch
import torch.nn as nn
import numpy as np
import random

def train_network(model, optimizer, training_data, device, epochs=10, batch_size=128):
    """训练神经网络"""
    criterion_policy = nn.CrossEntropyLoss()
    criterion_value = nn.MSELoss()
    
    for epoch in range(epochs):
        # 打乱数据
        random.shuffle(training_data)
        total_loss = 0
        policy_losses = 0
        value_losses = 0
        
        for i in range(0, len(training_data), batch_size):
            batch = training_data[i:i+batch_size]
            states, policy_targets, value_targets = zip(*batch)
            
            # 转换为张量并移至设备
            states = torch.FloatTensor(np.array(states)).to(device)
            policy_targets = torch.FloatTensor(np.array(policy_targets)).to(device)
            value_targets = torch.FloatTensor(np.array(value_targets)).unsqueeze(1).to(device)
            
            # 前向传播
            policy_logits, values = model(states)
            
            # 计算损失
            policy_loss = criterion_policy(policy_logits, policy_targets)
            value_loss = criterion_value(values, value_targets)
            loss = policy_loss + value_loss
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            policy_losses += policy_loss.item()
            value_losses += value_loss.item()
        
        print(f"Epoch {epoch+1}/{epochs}, Total Loss: {total_loss:.4f}, Policy Loss: {policy_losses:.4f}, Value Loss: {value_losses:.4f}")
    
    return model
