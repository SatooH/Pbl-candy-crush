import pygame
import random
import pickle
import sys

# Definindo constantes
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480
GRID_SIZE = 6
GEM_SIZE = SCREEN_WIDTH // GRID_SIZE

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GEM_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]

# Função para criar um tabuleiro inicial com gemas embaralhadas
def create_board():
    board = [[BLACK] * GRID_SIZE for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            board[row][col] = random.choice(GEM_COLORS)
    return board

# Função para verificar se uma troca é válida
def is_valid_swap(board, selected_gem, row, col):
    return abs(selected_gem[0] - row) + abs(selected_gem[1] - col) == 1

# Função para trocar a posição de duas gemas no tabuleiro
def swap_gems(board, row1, col1, row2, col2):
    if is_valid_swap(board, (row1, col1), row2, col2):
        board[row1][col1], board[row2][col2] = board[row2][col2], board[row1][col1]

# Função para desenhar o tabuleiro
def draw_board(screen, board):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            gem_color = board[row][col]
            pygame.draw.rect(screen, gem_color, pygame.Rect(col * GEM_SIZE, row * GEM_SIZE, GEM_SIZE, GEM_SIZE))

# Função para verificar se existe uma cadeia de gemas
def has_chain(board, row, col):
    color = board[row][col]
    return (
        (row > 1 and board[row - 1][col] == color and board[row - 2][col] == color) or
        (row < GRID_SIZE - 2 and board[row + 1][col] == color and board[row + 2][col] == color) or
        (col > 1 and board[row][col - 1] == color and board[row][col - 2] == color) or
        (col < GRID_SIZE - 2 and board[row][col + 1] == color and board[row][col + 2] == color)
    )

# Função para atualizar o tabuleiro após eliminar gemas
def update_board(board):
    for col in range(GRID_SIZE):
        empty_count = sum(1 for row in range(GRID_SIZE) if board[row][col] == BLACK)
        for row in range(GRID_SIZE - 1, -1, -1):
            if board[row][col] == BLACK:
                empty_count += 1
            else:
                board[row + empty_count][col] = board[row][col]
                if empty_count:
                    board[row][col] = BLACK

# Função para verificar e eliminar cadeias de gemas
def check_and_eliminate_chains(board):
    chains = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] != BLACK and has_chain(board, row, col):
                chains.append((row, col))
    return chains

# Função para calcular a pontuação com base nas cadeias eliminadas
def calculate_score(board, chains):
    score = 0
    for chain in chains:
        row, col = chain
        gem_color = board[row][col]
        chain_length = 1
        while col + chain_length < GRID_SIZE and board[row][col + chain_length] == gem_color:
            chain_length += 1
        if chain_length >= 3:
            score += chain_length * 2
            if chain_length >= 4:
                score *= 5
    return score

# Função para mostrar a tela de fim de jogo
def show_game_over_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    text_surface = font.render("Game Over", True, WHITE)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(text_surface, text_rect)

    font = pygame.font.Font(None, 24)
    restart_button = font.render("Restart", True, WHITE)
    restart_rect = restart_button.get_rect()
    restart_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
    screen.blit(restart_button, restart_rect)

    quit_button = font.render("Quit", True, WHITE)
    quit_rect = quit_button.get_rect()
    quit_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
    screen.blit(quit_button, quit_rect)

    pygame.display.flip()

    waiting_for_input = True

    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if restart_rect.collidepoint(mouse_x, mouse_y):
                    reset_game()
                    waiting_for_input = False
                elif quit_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()

# Função para redefinir o jogo
def reset_game():
    global board, score
    board = create_board()
    score = 0
    global game_state
    game_state = "playing"

# Função para verificar se o jogador atingiu a pontuação de 100 pontos
def check_win_condition(score):
    return score >= 100

# Função para gerar novas gemas no tabuleiro
def generate_new_gems(board):
    for col in range(GRID_SIZE):
        for row in range(GRID_SIZE):
            if board[row][col] == BLACK:
                board[row][col] = random.choice(GEM_COLORS)

# Loop principal do jogo
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Candy Crush Clone")

board = create_board()
selected_gem = None
score = 0

# Carregar dados do jogador
try:
    with open("player_data.pickle", "rb") as file:
        player_data = pickle.load(file)
except FileNotFoundError:
    player_data = {
        "wins": 0,
        "losses": 0,
        "total_score": 0
    }

clock = pygame.time.Clock()
running = True
game_state = "playing"  # Pode ser "playing" ou "game_over"
moves_remaining = 20  # Número de movimentos disponíveis

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // GEM_SIZE
                row = event.pos[1] // GEM_SIZE
                if selected_gem is None:
                    selected_gem = (row, col)
                else:
                    swap_gems(board, *selected_gem, row, col)
                    selected_gem = None
                    moves_remaining -= 1  # Deduzir um movimento

    if game_state == "playing":
        # Lógica do jogo acontece aqui
        chains = check_and_eliminate_chains(board)
        score += calculate_score(board, chains)
        update_board(board)
        
        if check_win_condition(score) or moves_remaining <= 0:
            game_state = "game_over"

        if len(chains) == 0:
            generate_new_gems(board)  # Gerar novas gemas se não houver cadeias

    elif game_state == "game_over":
        show_game_over_screen()

    # Salvar dados do jogador
    with open("player_data.pickle", "wb") as file:
        pickle.dump(player_data, file)

    # Atualizar a tela do jogo
    screen.fill(BLACK)
    draw_board(screen, board)
    pygame.display.flip()
    clock.tick(60)

# Encerrar o Pygame
pygame.quit()
