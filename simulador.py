# --- START OF FILE simulador.py ---

import pygame
import random
# Importa as classes do nosso módulo de modelo
from modelo import MapCell, Drone, Mission
# Importa a estrutura de dados para o histórico de missões
from estruturas import LinkedList

# =============================================================================
# CLASSE PRINCIPAL DA SIMULAÇÃO (CONTROLADOR E VISÃO)
# =============================================================================

class Simulator:
    """
    Classe principal que gerencia a simulação, a interface gráfica com Pygame
    e o estado geral da aplicação.
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Simulador de Missões de Drones")
        
        # Configurações do Mapa e Tela
        self.GRID_WIDTH, self.GRID_HEIGHT = 25, 20
        self.CELL_SIZE = 30
        self.UI_WIDTH = 400
        self.SCREEN_WIDTH = self.GRID_WIDTH * self.CELL_SIZE + self.UI_WIDTH
        self.SCREEN_HEIGHT = self.GRID_HEIGHT * self.CELL_SIZE
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Cores e Fontes
        self.COLORS = {
            'Urbana': (100, 100, 100), 'Residencial': (180, 180, 160),
            'Industrial': (50, 50, 60), 'Rural': (200, 220, 150),
            'Mata': (34, 139, 34), 'Zona de Risco': (255, 100, 100),
            'background': (20, 20, 40), 'ui_text': (240, 240, 240),
            'drone': (255, 255, 0), 'path': (0, 191, 255, 150)
        }
        self.FONT_S = pygame.font.SysFont("Consolas", 14)
        self.FONT_M = pygame.font.SysFont("Consolas", 16, bold=True)
        self.FONT_L = pygame.font.SysFont("Consolas", 20, bold=True)
        
        # Estado da Aplicação
        self.game_state = "MENU" # MENU, SIMULATING, STATS
        self.simulation_mode = "Manual" # Manual, Automatico
        self.mission_type = "Monitoramento" # Monitoramento, Entrega, Vigilância
        self.clock = pygame.time.Clock()
        self.running = True

        # Elementos da Simulação
        self.map_grid = [[MapCell() for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.drone = Drone(self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)
        self.current_mission = None
        self.completed_missions = LinkedList()
        
        # Para modo automático
        self.auto_path = []
        self.auto_path_index = 0
        self.last_auto_move_time = 0
        
    def generate_auto_path(self):
        """Gera um caminho simples (varredura) para o modo automático."""
        path = []
        for y in range(self.GRID_HEIGHT):
            if y % 2 == 0: # Move para a direita
                for x in range(self.GRID_WIDTH):
                    path.append((x, y))
            else: # Move para a esquerda
                for x in range(self.GRID_WIDTH - 1, -1, -1):
                    path.append((x, y))
        return path

    def start_simulation(self):
        """Inicia uma nova simulação, resetando e configurando os elementos."""
        self.drone = Drone(self.GRID_WIDTH // 2, self.GRID_HEIGHT // 2)
        self.current_mission = Mission(self.mission_type, self.drone)
        self.current_mission.start()
        
        # Coleta o ponto inicial
        initial_cell = self.map_grid[self.drone.y][self.drone.x]
        initial_data = self.drone.collect_data(initial_cell)
        self.current_mission.add_flight_point(initial_data)

        if self.simulation_mode == "Automatico":
            self.auto_path = self.generate_auto_path()
            self.auto_path_index = self.auto_path.index((self.drone.x, self.drone.y))
            self.last_auto_move_time = pygame.time.get_ticks()

        self.game_state = "SIMULATING"
        
    def end_simulation(self):
        if self.current_mission:
            self.current_mission.end()
            self.completed_missions.append(self.current_mission)
            self.current_mission = None
        self.game_state = "STATS"

    def run(self):
        """Loop principal da aplicação."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(30) # Limita o FPS
        pygame.quit()

    def handle_events(self):
        """Processa todas as entradas do usuário (teclado, mouse, etc.)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.game_state == "SIMULATING" and self.simulation_mode == "Manual":
                if event.type == pygame.KEYDOWN:
                    dx, dy = 0, 0
                    if event.key == pygame.K_LEFT and self.drone.x > 0: dx = -1
                    elif event.key == pygame.K_RIGHT and self.drone.x < self.GRID_WIDTH - 1: dx = 1
                    elif event.key == pygame.K_UP and self.drone.y > 0: dy = -1
                    elif event.key == pygame.K_DOWN and self.drone.y < self.GRID_HEIGHT - 1: dy = 1
                    
                    if dx != 0 or dy != 0:
                        self.drone.move(dx, dy, self.CELL_SIZE)
                        cell = self.map_grid[self.drone.y][self.drone.x]
                        data_point = self.drone.collect_data(cell)
                        self.current_mission.add_flight_point(data_point)
                    
                    if event.key == pygame.K_c:
                        self.drone.toggle_camera()
                    if event.key == pygame.K_p:
                        self.drone.take_photo()
                    if event.key == pygame.K_ESCAPE:
                        self.end_simulation()
            
            elif self.game_state == "SIMULATING" and self.simulation_mode == "Automatico":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.end_simulation()

            elif self.game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.simulation_mode = "Manual"
                    if event.key == pygame.K_2: self.simulation_mode = "Automatico"
                    if event.key == pygame.K_q: self.mission_type = "Monitoramento"
                    if event.key == pygame.K_w: self.mission_type = "Entrega"
                    if event.key == pygame.K_e: self.mission_type = "Vigilância"
                    if event.key == pygame.K_RETURN: self.start_simulation()
            
            elif self.game_state == "STATS":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.game_state = "MENU"

    def update(self):
        """Atualiza a lógica do jogo (ex: movimento automático do drone)."""
        if self.game_state == "SIMULATING":
            # Condição para fim de missão
            if self.drone.battery <= 0:
                self.end_simulation()
                return

            if self.simulation_mode == "Automatico":
                current_time = pygame.time.get_ticks()
                if current_time - self.last_auto_move_time > 200: # Move a cada 200ms
                    self.last_auto_move_time = current_time
                    self.auto_path_index += 1
                    if self.auto_path_index < len(self.auto_path):
                        next_pos = self.auto_path[self.auto_path_index]
                        dx = next_pos[0] - self.drone.x
                        dy = next_pos[1] - self.drone.y
                        
                        self.drone.move(dx, dy, self.CELL_SIZE)
                        cell = self.map_grid[self.drone.y][self.drone.x]
                        data_point = self.drone.collect_data(cell)
                        self.current_mission.add_flight_point(data_point)
                        
                        # Simula ações automáticas baseadas na missão
                        if self.mission_type == "Vigilância" and random.random() < 0.1:
                            self.drone.take_photo()

                    else: # Fim do caminho
                        self.end_simulation()

    # MÉTODOS DE DESENHO (VISÃO)
    def draw_text(self, text, font, color, x, y, center=False):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_map(self):
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                rect = pygame.Rect(x * self.CELL_SIZE, y * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                cell_type = self.map_grid[y][x].area_type
                pygame.draw.rect(self.screen, self.COLORS[cell_type], rect)
                pygame.draw.rect(self.screen, (50, 50, 50), rect, 1) # Borda da célula

    def draw_flight_path(self):
        if self.current_mission and not self.current_mission.flight_path.is_empty():
            path_points = []
            for point in self.current_mission.flight_path:
                coords = point.telemetry['coords']
                center_x = coords[0] * self.CELL_SIZE + self.CELL_SIZE // 2
                center_y = coords[1] * self.CELL_SIZE + self.CELL_SIZE // 2
                path_points.append((center_x, center_y))
            
            if len(path_points) > 1:
                pygame.draw.lines(self.screen, self.COLORS['path'], False, path_points, 3)

    def draw_drone(self):
        center_x = self.drone.x * self.CELL_SIZE + self.CELL_SIZE // 2
        center_y = self.drone.y * self.CELL_SIZE + self.CELL_SIZE // 2
        pygame.draw.circle(self.screen, self.COLORS['drone'], (center_x, center_y), self.CELL_SIZE // 3)
        # Indicação de carga
        if self.drone.payload_status:
             pygame.draw.rect(self.screen, (0, 255, 0), (center_x-5, center_y+5, 10, 5))
        # Indicação de câmera
        if self.drone.camera_status:
             pygame.draw.circle(self.screen, (255, 0, 0), (center_x, center_y), 3)

    def draw_ui(self):
        ui_x = self.GRID_WIDTH * self.CELL_SIZE
        ui_rect = pygame.Rect(ui_x, 0, self.UI_WIDTH, self.SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, self.COLORS['background'], ui_rect)
        
        y_pos = 20
        
        # Título
        self.draw_text("TELEMETRIA E AMBIENTE", self.FONT_L, self.COLORS['ui_text'], ui_x + self.UI_WIDTH/2, y_pos, center=True)
        y_pos += 40

        # Dados do Drone (Telemetria)
        if self.game_state == "SIMULATING":
            last_point = list(self.current_mission.flight_path)[-1]
            telemetry = last_point.telemetry
            env = last_point.environment

            self.draw_text("--- DRONE ---", self.FONT_M, self.COLORS['drone'], ui_x + 10, y_pos); y_pos += 20
            for key, val in telemetry.items():
                self.draw_text(f"{key.replace('_', ' ').title()}: {val}", self.FONT_S, self.COLORS['ui_text'], ui_x + 15, y_pos); y_pos += 18
            
            y_pos += 10
            # Dados do Ambiente
            self.draw_text("--- AMBIENTE ---", self.FONT_M, (100, 200, 255), ui_x + 10, y_pos); y_pos += 20
            for key, val in env.items():
                self.draw_text(f"{key.replace('_', ' ').title()}: {val}", self.FONT_S, self.COLORS['ui_text'], ui_x + 15, y_pos); y_pos += 18

            y_pos += 20
            self.draw_text(f"Missão: {self.mission_type} ({self.simulation_mode})", self.FONT_M, (255,165,0), ui_x + 10, y_pos); y_pos += 25
            self.draw_text("Pressione ESC para finalizar missão", self.FONT_S, (255,100,100), ui_x + 10, y_pos)

    def draw_menu(self):
        self.screen.fill(self.COLORS['background'])
        y_pos = 100
        self.draw_text("SIMULADOR DE DRONES", self.FONT_L, self.COLORS['drone'], self.SCREEN_WIDTH/2, y_pos, center=True); y_pos += 80

        self.draw_text("1. Modo de Simulação:", self.FONT_M, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 30
        self.draw_text(f"   [1] Manual {'<' if self.simulation_mode == 'Manual' else ''}", self.FONT_S, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 25
        self.draw_text(f"   [2] Automático {'<' if self.simulation_mode == 'Automatico' else ''}", self.FONT_S, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 40

        self.draw_text("2. Tipo de Missão:", self.FONT_M, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 30
        self.draw_text(f"   [Q] Monitoramento Ambiental {'<' if self.mission_type == 'Monitoramento' else ''}", self.FONT_S, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 25
        self.draw_text(f"   [W] Entrega de Pacotes {'<' if self.mission_type == 'Entrega' else ''}", self.FONT_S, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 25
        self.draw_text(f"   [E] Vigilância {'<' if self.mission_type == 'Vigilância' else ''}", self.FONT_S, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 150, y_pos); y_pos += 80

        self.draw_text("Pressione ENTER para INICIAR", self.FONT_M, self.COLORS['drone'], self.SCREEN_WIDTH/2, y_pos, center=True)

    def draw_stats(self):
        self.screen.fill(self.COLORS['background'])
        last_mission = list(self.completed_missions)[-1]
        stats = last_mission.calculate_statistics()
        
        y_pos = 100
        self.draw_text("MISSÃO CONCLUÍDA", self.FONT_L, self.COLORS['drone'], self.SCREEN_WIDTH/2, y_pos, center=True); y_pos += 60
        self.draw_text(f"Tipo: {last_mission.mission_type}", self.FONT_M, self.COLORS['ui_text'], self.SCREEN_WIDTH/2, y_pos, center=True); y_pos += 50
        
        self.draw_text("--- ESTATÍSTICAS FINAIS ---", self.FONT_M, (100, 200, 255), self.SCREEN_WIDTH/2, y_pos, center=True); y_pos += 40
        
        if not stats:
            self.draw_text("Dados insuficientes para gerar estatísticas.", self.FONT_S, (255,100,100), self.SCREEN_WIDTH/2, y_pos, center=True)
        else:
            for key, val in stats.items():
                self.draw_text(f"{key}: {val}", self.FONT_M, self.COLORS['ui_text'], self.SCREEN_WIDTH/2 - 200, y_pos)
                y_pos += 35
        
        y_pos += 50
        self.draw_text("Pressione ENTER para voltar ao Menu", self.FONT_M, self.COLORS['drone'], self.SCREEN_WIDTH/2, y_pos, center=True)

    def draw(self):
        """Função principal de desenho, que chama outras funções de acordo com o estado."""
        self.screen.fill(self.COLORS['background'])
        
        if self.game_state == "SIMULATING":
            self.draw_map()
            self.draw_flight_path()
            self.draw_drone()
            self.draw_ui()
        elif self.game_state == "MENU":
            self.draw_menu()
        elif self.game_state == "STATS":
            self.draw_stats()
            
        pygame.display.flip()
        
# --- END OF FILE simulador.py ---