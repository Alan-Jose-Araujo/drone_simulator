# --- START OF FILE modelo.py ---

import random
import math
import time
# Importa a estrutura de dados do nosso módulo local
from estruturas import LinkedList

# =============================================================================
# CLASSES DO MODELO DA SIMULAÇÃO (ORIENTAÇÃO A OBJETOS)
# =============================================================================

class MapCell:
    """Representa uma célula no mapa com suas características ambientais."""
    def __init__(self):
        self.area_type = random.choice(['Urbana', 'Residencial', 'Industrial', 'Rural', 'Mata', 'Zona de Risco'])
        self.population_density = random.randint(50, 15000)  # hab/km²
        self.green_area_percent = random.randint(0, 100) if self.area_type in ['Rural', 'Mata', 'Residencial'] else random.randint(0, 20)
        self.air_pollution_index = random.randint(0, 300) # Valor do índice
        self.has_tall_buildings = random.choice([True, False]) if self.area_type in ['Urbana', 'Industrial'] else False
        self.gps_signal = random.choice(['Forte', 'Fraco', 'Perdido'])
        self.noise_level = random.randint(30, 110) # dB

class DataPoint:
    """Armazena todos os dados coletados em um único ponto de voo."""
    def __init__(self, telemetry_data, environment_data):
        self.telemetry = telemetry_data
        self.environment = environment_data
        self.timestamp = time.time()

class Drone:
    """Representa o drone, seu estado e suas capacidades."""
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.altitude = random.randint(50, 150) # metros
        self.speed = 0 # m/s
        self.wind_direction = random.randint(0, 360)
        self.battery = 100.0 # %
        self.ambient_temperature = random.uniform(15.0, 35.0)
        self.payload_status = False # False: sem pacote
        self.camera_status = False # False: desligada
        self.photos_taken = 0
        self.missions_history = LinkedList() # Histórico de missões do drone

    def move(self, dx, dy, grid_size):
        """Movimenta o drone e consome bateria."""
        if self.battery > 0:
            self.x += dx
            self.y += dy
            # Consome mais bateria se o movimento for na diagonal
            distance_moved = math.sqrt(dx**2 + dy**2)
            self.battery -= 0.1 * distance_moved # Custo de bateria por célula movida
            self.battery = max(0, self.battery) # Garante que a bateria não seja negativa
            self.speed = 10 * distance_moved # Simulação de velocidade (10 m/s por célula)

    def collect_data(self, map_cell: MapCell):
        """Coleta dados de telemetria e do ambiente e cria um DataPoint."""
        telemetry = {
            "coords": (self.x, self.y),
            "altitude": self.altitude,
            "speed": self.speed,
            "wind_direction": self.wind_direction,
            "battery": round(self.battery, 2),
            "temperature": round(self.ambient_temperature, 1),
            "payload_status": "Com Pacote" if self.payload_status else "Sem Pacote",
            "camera_status": "Ligada" if self.camera_status else "Desligada",
            "photos_taken": self.photos_taken
        }
        environment = {
            "area_type": map_cell.area_type,
            "population_density": map_cell.population_density,
            "green_area_percent": map_cell.green_area_percent,
            "air_pollution_index": map_cell.air_pollution_index,
            "has_tall_buildings": "Sim" if map_cell.has_tall_buildings else "Não",
            "gps_signal": map_cell.gps_signal,
            "noise_level": map_cell.noise_level
        }
        return DataPoint(telemetry, environment)
        
    def toggle_camera(self):
        self.camera_status = not self.camera_status
    
    def take_photo(self):
        if self.camera_status and self.battery > 0.05:
            self.photos_taken += 1
            self.battery -= 0.05 # Custo de tirar foto

class Mission:
    """Gerencia uma missão específica, seu tipo, status e dados de voo."""
    def __init__(self, mission_type, drone: Drone):
        self.mission_type = mission_type
        self.drone = drone
        self.flight_path = LinkedList() # A lista encadeada para os dados de voo
        self.start_time = None
        self.end_time = None
        self.status = "Não iniciada"
        self.initial_battery = drone.battery
        self.final_battery = None

    def start(self):
        self.start_time = time.time()
        self.status = "Em andamento"
        # Configurações iniciais baseadas na missão
        if self.mission_type == "Entrega":
            self.drone.payload_status = True
        elif self.mission_type == "Vigilância":
            self.drone.toggle_camera()
    
    def add_flight_point(self, data_point: DataPoint):
        self.flight_path.append(data_point)

    def end(self):
        self.end_time = time.time()
        self.status = f"Concluída"
        self.final_battery = self.drone.battery
        if self.drone.payload_status: # Se era entrega, solta o pacote no final
            self.drone.payload_status = False
        if self.drone.camera_status: # Desliga a camera no final
            self.drone.toggle_camera()
        
    def calculate_statistics(self):
        """Calcula as estatísticas da missão a partir dos dados na lista encadeada."""
        if len(self.flight_path) < 2 or self.final_battery is None:
            return {}

        total_distance = 0
        total_pollution = 0
        total_population = 0
        
        points = list(self.flight_path) # Converte para lista temporária para fácil acesso por índice
        
        for i in range(len(points) - 1):
            p1 = points[i].telemetry['coords']
            p2 = points[i+1].telemetry['coords']
            total_distance += math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            
        for point in self.flight_path:
            total_pollution += point.environment['air_pollution_index']
            total_population += point.environment['population_density']

        mission_duration = self.end_time - self.start_time
        battery_consumed = self.initial_battery - self.final_battery
        energy_efficiency = battery_consumed / total_distance if total_distance > 0 else 0

        # Área coberta por vegetação: Simplificado como a média do percentual nas áreas sobrevoadas
        total_green_area_percent = sum(p.environment['green_area_percent'] for p in self.flight_path)
        
        return {
            "Distância Total (células)": round(total_distance, 2),
            "Tempo Total (s)": round(mission_duration, 2),
            "Média Poluição do Ar": round(total_pollution / len(self.flight_path), 2),
            "Média Densidade Populacional": round(total_population / len(self.flight_path), 2),
            "Média Cobertura Vegetal (%)": round(total_green_area_percent / len(self.flight_path), 2),
            "Eficiência Energética (%/célula)": round(energy_efficiency, 3)
        }

# --- END OF FILE modelo.py ---