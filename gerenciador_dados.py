# --- START OF FILE gerenciador_dados.py ---

import json
import os
import time

from estruturas import LinkedList
from modelo import Mission, DataPoint, Drone

def missions_to_dict_list(missions_linked_list: LinkedList):
    """Converte uma LinkedList de Missões para uma lista de dicionários serializáveis."""
    output_list = []
    for mission in missions_linked_list:
        # Converte o caminho de voo (LinkedList de DataPoints) para uma lista de dicionários
        flight_path_list = []
        for point in mission.flight_path:
            flight_path_list.append({
                "telemetry": point.telemetry,
                "environment": point.environment,
                "timestamp": point.timestamp
            })
        
        # Cria o dicionário da missão
        mission_dict = {
            "mission_type": mission.mission_type,
            "start_time": mission.start_time,
            "end_time": mission.end_time,
            "status": mission.status,
            "initial_battery": mission.initial_battery,
            "final_battery": getattr(mission, 'final_battery', None), # Usa getattr para ser seguro
            "flight_path": flight_path_list
        }
        output_list.append(mission_dict)
    return output_list

def dict_list_to_missions(data: list):
    """Converte uma lista de dicionários (do JSON) para uma LinkedList de Missões."""
    missions_ll = LinkedList()
    for mission_dict in data:
        # Criamos um drone "dummy" apenas para instanciar a Missão. 
        # A lógica de estatísticas usará os valores salvos, não este drone.
        dummy_drone = Drone(0, 0)

        # Recria o objeto Mission
        mission = Mission(mission_dict['mission_type'], dummy_drone)
        mission.start_time = mission_dict['start_time']
        mission.end_time = mission_dict['end_time']
        mission.status = mission_dict['status']
        mission.initial_battery = mission_dict['initial_battery']
        mission.final_battery = mission_dict['final_battery']

        # Recria a flight_path (LinkedList de DataPoints)
        for point_dict in mission_dict['flight_path']:
            dp = DataPoint(point_dict['telemetry'], point_dict['environment'])
            dp.timestamp = point_dict['timestamp']
            mission.add_flight_point(dp)
        
        missions_ll.append(mission)
    return missions_ll

def save_missions(missions: LinkedList, filename: str):
    """Salva a lista de missões completas em um arquivo JSON."""
    missions_data = missions_to_dict_list(missions)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(missions_data, f, indent=4, ensure_ascii=False)
        print(f"Histórico de missões salvo em {filename}")
    except IOError as e:
        print(f"Erro ao salvar o arquivo de histórico: {e}")

def load_missions(filename: str):
    """Carrega o histórico de missões de um arquivo JSON."""
    if not os.path.exists(filename):
        return LinkedList() # Retorna uma lista vazia se o arquivo não existe

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # A conversão é feita do mais antigo para o mais novo
        missions_ll = dict_list_to_missions(data)
        print(f"Histórico de missões carregado de {filename}")
        return missions_ll
    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar ou decodificar o arquivo de histórico: {e}")
        return LinkedList() # Retorna lista vazia em caso de erro

# --- END OF FILE gerenciador_dados.py ---