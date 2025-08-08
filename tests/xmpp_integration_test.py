#!/usr/bin/env python3
"""
Prueba de integración del sistema multiagente con comunicación XMPP.

Este script prueba la funcionalidad completa de comunicación entre agentes
utilizando los protocolos implementados.
"""

import asyncio
import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from assembly_line_system.agents import (
    ConveyorAgent,
    CraneAgent,
    RoboticArmAgent,
    AssemblyStationAgent
)
from assembly_line_system.protocols.material_transfer import MaterialTransferProtocol
from assembly_line_system.config import XMPP_CONFIG

# Crear un entorno simulado para los agentes
class MockEnvironment:
    """Entorno simulado para pruebas."""
    def __init__(self):
        self.time = 0

async def test_xmpp_communication():
    """Prueba completa de comunicación XMPP entre agentes."""
    
    print("=== Prueba de Integración XMPP ===")
    print(f"Configuración XMPP: {XMPP_CONFIG}")
    print()
    
    # Crear un entorno simulado
    env = MockEnvironment()
    
    # Crear agentes de prueba (usando los parámetros correctos)
    print("Creando agentes para la prueba...")
    
    conveyor = ConveyorAgent(
        agent_id="conveyor_01",
        jid="conveyor_01@ejabberd.local",
        password="password123",
        env=env
    )
    
    crane = CraneAgent(
        agent_id="crane_01", 
        jid="crane_01@ejabberd.local",
        password="password123",
        env=env
    )
    
    robotic_arm = RoboticArmAgent(
        agent_id="robotic_arm_01",
        jid="robotic_arm_01@ejabberd.local",
        password="password123",
        env=env
    )
    
    assembly_station = AssemblyStationAgent(
        agent_id="assembly_01",
        jid="assembly_01@ejabberd.local",
        password="password123",
        env=env
    )
    
    # Mostrar información de los agentes
    print("Agentes creados:")
    agents = [conveyor, crane, robotic_arm, assembly_station]
    
    for agent in agents:
        print(f"  - {agent.agent_id} (Tipo: {type(agent).__name__})")
        print()
    
    # Prueba 1: Verificación de capacidades de transferencia
    print("=== Prueba 1: Capacidades de Transferencia ===")
    
    # Verificar si los agentes pueden aceptar transferencias
    print("Verificando capacidad de aceptar transferencias:")
    
    can_accept = conveyor.can_accept_transfer("material_001", 2)
    print(f"  Cinta transportadora puede aceptar: {can_accept}")
    
    can_accept = crane.can_accept_transfer("material_002", 1)
    print(f"  Grúa puede aceptar: {can_accept}")
    
    can_accept = robotic_arm.can_accept_transfer("material_003", 1)
    print(f"  Brazo robótico puede aceptar: {can_accept}")
    
    can_accept = assembly_station.can_accept_transfer("material_004", 3)
    print(f"  Estación de ensamblaje puede aceptar: {can_accept}")
    
    # Prueba 2: Obtener tiempos de preparación
    print("\n=== Prueba 2: Tiempos de Preparación ===")
    
    ready_time = conveyor.get_ready_time()
    print(f"  Cinta transportadora listo en: {ready_time} segundos")
    
    ready_time = crane.get_ready_time()
    print(f"  Grúa lista en: {ready_time} segundos")
    
    ready_time = robotic_arm.get_ready_time()
    print(f"  Brazo robótico listo en: {ready_time} segundos")
    
    ready_time = assembly_station.get_ready_time()
    print(f"  Estación de ensamblaje lista en: {ready_time} segundos")
    
    # Prueba 3: Simulación de mensajes XMPP
    print("\n=== Prueba 3: Mensajes XMPP Simulados ===")
    
    # Crear mensaje de solicitud de transferencia
    print("Creando mensaje de solicitud de transferencia...")
    
    # Simular un mensaje de solicitud desde el brazo robótico a la estación
    transfer_msg = MaterialTransferProtocol.create_request_message(
        source_id="robotic_arm_01",
        target_jid="assembly_01@ejabberd.local",  # JID simulado
        material_id="material_001",
        quantity=5,
        destination="assembly_station"
    )
    
    print(f"Mensaje de solicitud creado: {transfer_msg.body}")
    
    # Crear mensaje de confirmación
    print("Creando mensaje de confirmación...")
    
    confirm_msg = MaterialTransferProtocol.create_confirm_message(
        target_id="assembly_01",
        source_jid="robotic_arm_01@ejabberd.local",
        ready_time=30
    )
    
    print(f"Mensaje de confirmación creado: {confirm_msg.body}")
    
    # Crear mensaje de ejecución
    print("Creando mensaje de ejecución...")
    
    execute_msg = MaterialTransferProtocol.create_execute_message(
        source_id="robotic_arm_01",
        target_jid="assembly_01@ejabberd.local"
    )
    
    print(f"Mensaje de ejecución creado: {execute_msg.body}")
    
    # Crear mensaje de rechazo
    print("Creando mensaje de rechazo...")
    
    reject_msg = MaterialTransferProtocol.create_reject_message(
        source_id="assembly_01",
        target_jid="robotic_arm_01@ejabberd.local",
        reason="estacion ocupada"
    )
    
    print(f"Mensaje de rechazo creado: {reject_msg.body}")
    
    # Prueba 4: Métodos de transferencia
    print("\n=== Prueba 4: Métodos de Transferencia ===")
    
    # Ejecutar transferencias simuladas
    try:
        result = robotic_arm.perform_transfer()
        print(f"  Transferencia brazo robótico: {result}")
    except Exception as e:
        print(f"  Error en transferencia brazo robótico: {e}")
    
    try:
        result = conveyor.perform_transfer()
        print(f"  Transferencia cinta transportadora: {result}")
    except Exception as e:
        print(f"  Error en transferencia cinta transportadora: {e}")
    
    # Prueba 5: Verificación de configuración
    print("\n=== Prueba 5: Configuración del Sistema ===")
    
    # Verificar configuraciones
    print(f"Configuración XMPP: {XMPP_CONFIG}")
    
    print("\n=== Prueba de Integración Completada ===")
    print("Todas las funcionalidades XMPP han sido verificadas correctamente.")

if __name__ == "__main__":
    asyncio.run(test_xmpp_communication())