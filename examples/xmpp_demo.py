#!/usr/bin/env python3
"""
Demostración de uso del sistema de línea de ensamblaje multiagente con XMPP.

Este script muestra cómo se pueden crear y coordinar agentes
utilizando la comunicación XMPP.
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
from assembly_line_system.config import XMPP_CONFIG, AGENT_TYPES

async def main():
    """Función principal de demostración."""
    
    print("=== Demostración del Sistema Multiagente ===")
    print(f"Configuración XMPP: {XMPP_CONFIG}")
    print()
    
    # Crear agentes de ejemplo
    print("Creando agentes...")
    
    # Agente de cinta transportadora
    conveyor = ConveyorAgent(
        agent_id="conveyor_01",
        jid="conveyor_01@ejabberd.local",
        password="password123",
        env=None
    )
    
    # Agente de grúa
    crane = CraneAgent(
        agent_id="crane_01",
        jid="crane_01@ejabberd.local",
        password="password123",
        env=None
    )
    
    # Agente de brazo robótico
    robotic_arm = RoboticArmAgent(
        agent_id="robotic_arm_01",
        jid="robotic_arm_01@ejabberd.local",
        password="password123",
        env=None
    )
    
    # Agente de estación de ensamblaje
    assembly_station = AssemblyStationAgent(
        agent_id="assembly_01",
        jid="assembly_01@ejabberd.local",
        password="password123",
        env=None
    )
    
    # Mostrar información de los agentes
    print("Agentes creados:")
    agents = [conveyor, crane, robotic_arm, assembly_station]
    
    for agent in agents:
        print(f"  - {agent.agent_id} (Tipo: {type(agent).__name__})")
        print()
    
    # Demostrar métodos de comunicación XMPP
    print("=== Métodos de Comunicación XMPP ===")
    
    # Ejemplo de verificación de aceptación de transferencia
    print("Verificando capacidad de aceptar transferencias:")
    
    # Verificar si el agente puede aceptar una transferencia
    can_accept = conveyor.can_accept_transfer("material_001", 2)
    print(f"  Cinta transportadora puede aceptar: {can_accept}")
    
    # Obtener tiempo de preparación
    ready_time = conveyor.get_ready_time()
    print(f"  Tiempo de preparación: {ready_time} segundos")
    
    # Ejemplo de transferencia (simulada)
    print("\nSimulando transferencia de materiales:")
    
    # El brazo robótico intenta realizar una transferencia
    try:
        result = robotic_arm.perform_transfer("material_001", "assembly_01")
        print(f"  Transferencia realizada: {result}")
    except Exception as e:
        print(f"  Error en transferencia: {e}")
    
    # Ejemplo de mensaje XMPP (simulado)
    print("\n=== Mensajes XMPP Simulados ===")
    
    # Crear mensaje de solicitud de transferencia
    transfer_msg = {
        'type': 'transfer_request',
        'from_agent': 'robotic_arm_01',
        'to_agent': 'assembly_01',
        'material_id': 'material_001',
        'priority': 'high'
    }
    
    print(f"Mensaje de solicitud: {transfer_msg}")
    
    # Crear mensaje de respuesta
    response_msg = {
        'type': 'transfer_response',
        'from_agent': 'assembly_01',
        'to_agent': 'robotic_arm_01', 
        'status': 'accepted',
        'message': 'Transferencia aceptada'
    }
    
    print(f"Mensaje de respuesta: {response_msg}")
    
    # Ejemplo de manejo de rechazo
    print("\n=== Manejo de Rechazos ===")
    
    # Simular rechazo de transferencia
    rejection_msg = {
        'type': 'transfer_rejection',
        'from_agent': 'assembly_01',
        'to_agent': 'robotic_arm_01',
        'reason': 'estacion ocupada',
        'retry_after': 30
    }
    
    print(f"Mensaje de rechazo: {rejection_msg}")
    
    print("\n=== Demostración completada ===")

if __name__ == "__main__":
    asyncio.run(main())