import pygame
import sys
import os
from cn_chess import ChineseChess

# 初始化pygame
pygame.init()

# 设置游戏窗口
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 800
BOARD_SIZE = 600
GRID_SIZE = BOARD_SIZE // 9  # 每个格子的大小（宽度）
GRID_HEIGHT = BOARD_SIZE // 10  # 格子的高度

# 定义颜色
BACKGROUND_COLOR = (238, 215, 170)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SELECTED_COLOR = (0, 255, 0, 128)  # 选中棋子的高亮颜色

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('中国象棋')

# 加载图像
def load_images():
    images = {}
    # 加载棋盘
    board_img = pygame.image.load(os.path.join('resources', 'board.png'))
    board_img = pygame.transform.scale(board_img, (BOARD_SIZE, BOARD_SIZE))
    images['board'] = board_img
    
    # 加载棋子图像
    piece_names = {
        1: 'r_ju', 2: 'r_ma', 3: 'r_xiang', 4: 'r_shi', 5: 'r_shuai', 6: 'r_pao', 7: 'r_bing',
        -1: 'b_ju', -2: 'b_ma', -3: 'b_xiang', -4: 'b_shi', -5: 'b_jiang', -6: 'b_pao', -7: 'b_zu'
    }
    
    for piece_id, name in piece_names.items():
        img = pygame.image.load(os.path.join('resources', f'{name}.png'))
        img = pygame.transform.scale(img, (GRID_SIZE - 10, GRID_SIZE - 10))
        images[piece_id] = img
        
    return images

# 创建必要的资源目录
if not os.path.exists('resources'):
    os.makedirs('resources')
    print("请在 resources 文件夹中添加必要的图片资源")

# 绘制棋盘
def draw_board(screen, board_img):
    offset_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
    offset_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
    screen.fill(BACKGROUND_COLOR)
    screen.blit(board_img, (offset_x, offset_y))

# 绘制棋子
def draw_pieces(screen, game, images, selected_pos=None):
    offset_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
    offset_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
    
    for row in range(10):
        for col in range(9):
            piece = game.board[row, col]
            if piece != 0:
                piece_img = images[piece]
                pos_x = offset_x + col * GRID_SIZE + (GRID_SIZE - piece_img.get_width()) // 2
                pos_y = offset_y + row * GRID_HEIGHT + (GRID_HEIGHT - piece_img.get_height()) // 2
                
                # 绘制棋子
                screen.blit(piece_img, (pos_x, pos_y))
                
                # 如果是选中的棋子，添加高亮效果
                if selected_pos and selected_pos == (row, col):
                    s = pygame.Surface((piece_img.get_width(), piece_img.get_height()), pygame.SRCALPHA)
                    s.fill(SELECTED_COLOR)
                    screen.blit(s, (pos_x, pos_y))

# 绘制可能的移动位置
def draw_possible_moves(screen, possible_moves):
    offset_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
    offset_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
    
    for move in possible_moves:
        row, col = move
        pos_x = offset_x + col * GRID_SIZE + GRID_SIZE // 2
        pos_y = offset_y + row * GRID_HEIGHT + GRID_HEIGHT // 2
        
        # 绘制可能移动位置的标记
        pygame.draw.circle(screen, RED, (pos_x, pos_y), 5)

# 显示当前玩家
def draw_current_player(screen, current_player):
    font = pygame.font.SysFont('simhei', 24)
    if current_player == 1:
        text = font.render("红方走棋", True, RED)
    else:
        text = font.render("黑方走棋", True, BLACK)
    screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 20))

# 显示游戏结束信息
def draw_game_over(screen, winner):
    font = pygame.font.SysFont('simhei', 32)
    if winner == 1:
        text = font.render("红方胜利!", True, RED)
    elif winner == -1:
        text = font.render("黑方胜利!", True, BLACK)
    else:
        text = font.render("平局!", True, BLACK)
    
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    
    # 绘制半透明背景
    s = pygame.Surface((300, 100), pygame.SRCALPHA)
    s.fill((255, 255, 255, 200))
    screen.blit(s, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 50))
    
    screen.blit(text, text_rect)
    
    # 添加重新开始游戏的提示
    restart_font = pygame.font.SysFont('simhei', 24)
    restart_text = restart_font.render("按R键重新开始游戏", True, BLACK)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
    screen.blit(restart_text, restart_rect)

# 将屏幕坐标转换为棋盘坐标
def screen_to_board_pos(pos):
    x, y = pos
    offset_x = (WINDOW_WIDTH - BOARD_SIZE) // 2
    offset_y = (WINDOW_HEIGHT - BOARD_SIZE) // 2
    
    if x < offset_x or x > offset_x + BOARD_SIZE or y < offset_y or y > offset_y + BOARD_SIZE:
        return None  # 点击位置不在棋盘上
    
    col = (x - offset_x) // GRID_SIZE
    row = (y - offset_y) // GRID_HEIGHT
    
    if 0 <= row < 10 and 0 <= col < 9:
        return (row, col)
    return None

def main():
    # 初始化游戏
    game = ChineseChess()
    
    try:
        # 加载图像
        images = load_images()
    except pygame.error as e:
        print(f"无法加载图像: {e}")
        print("请确保 'resources' 文件夹中包含所需的图像")
        return
    
    # 游戏状态变量
    selected_pos = None
    possible_moves = []
    
    # 主游戏循环
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # 按R键重新开始游戏
                game = ChineseChess()
                selected_pos = None
                possible_moves = []
            
            if not game.is_game_over():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
                    board_pos = screen_to_board_pos(event.pos)
                    
                    if board_pos:
                        row, col = board_pos
                        piece = game.get_piece_id(board_pos)  # 使用get_piece_id而不是直接访问board
                        
                        # 如果已经选中了一个棋子，尝试移动
                        if selected_pos:
                            if board_pos in possible_moves:
                                # 尝试移动棋子
                                if game.make_move(selected_pos, board_pos):
                                    # 移动成功，清除选择
                                    selected_pos = None
                                    possible_moves = []
                                else:
                                    # 移动失败，可能是因为造成自己被将军
                                    print("非法移动")
                            elif piece != 0 and game.is_same_side(piece, game.current_player * 1):  # 使用is_same_side方法
                                # 选择了己方的另一个棋子，更新选择
                                selected_pos = board_pos
                                possible_moves = game.get_valid_moves(selected_pos)
                            else:
                                # 点击了空位或敌方棋子，但不是合法移动，清除选择
                                selected_pos = None
                                possible_moves = []
                        else:
                            # 如果还没有选中棋子，且点击了自己的棋子
                            if piece != 0 and game.is_same_side(piece, game.current_player * 1):  # 使用is_same_side方法
                                selected_pos = board_pos
                                possible_moves = game.get_valid_moves(selected_pos)
        
        # 绘制游戏
        draw_board(screen, images['board'])
        draw_pieces(screen, game, images, selected_pos)
        draw_possible_moves(screen, possible_moves)
        draw_current_player(screen, game.current_player)
        
        # 如果游戏结束，显示结果
        if game.is_game_over():
            draw_game_over(screen, game.get_winner())
        
        # 更新屏幕
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
