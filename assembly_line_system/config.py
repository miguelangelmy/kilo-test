"""
Configuración del sistema de línea de ensamblaje multiagente.

Este módulo contiene la configuración estándar para
la comunicación XMPP y los parámetros del sistema.
"""

# Configuración de XMPP
XMPP_CONFIG = {
    'server': 'localhost',
    'port': 5222,
    'domain': 'ejabberd.local',
    'admin_user': 'admin',
    'admin_password': 'secreta'
}

# Configuración del sistema
SYSTEM_CONFIG = {
    'max_retries': 3,
    'timeout_seconds': 30,
    'heartbeat_interval': 60
}

# Tipos de agentes disponibles
AGENT_TYPES = {
    'conveyor': 'ConveyorAgent',
    'crane': 'CraneAgent', 
    'robotic_arm': 'RoboticArmAgent',
    'assembly_station': 'AssemblyStationAgent'
}

# Configuración de los agentes
AGENT_CONFIG = {
    'conveyor': {
        'name': 'ConveyorAgent',
        'description': 'Agente de cinta transportadora',
        'capabilities': ['material_transfer', 'status_monitoring']
    },
    'crane': {
        'name': 'CraneAgent',
        'description': 'Agente de grúa',
        'capabilities': ['material_transfer', 'heavy_lifting']
    },
    'robotic_arm': {
        'name': 'RoboticArmAgent',
        'description': 'Agente de brazo robótico',
        'capabilities': ['material_transfer', 'precise_movement']
    },
    'assembly_station': {
        'name': 'AssemblyStationAgent',
        'description': 'Agente de estación de ensamblaje',
        'capabilities': ['material_transfer', 'assembly_operations']
    }
}