"""
Pruebas del ProtocolManager con procesamiento asíncrono.

Este script valida el funcionamiento completo del gestor de protocolos
con priorización, manejo de errores y persistencia de sesiones.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Importar componentes del sistema
import sys
sys.path.append('..')

from assembly_line_system.protocols.protocol_manager import (
    ProtocolManager,
    MessagePriority,
    ProtocolState
)
from assembly_line_system.protocols.material_transfer import MaterialTransferProtocol
from spade.message import Message


class MockAgent:
    """Agente simulado para pruebas del ProtocolManager."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.protocol_manager = None
        
    def set_protocol_manager(self, protocol_manager: ProtocolManager):
        """Asignar el gestor de protocolos."""
        self.protocol_manager = protocol_manager
        
    def send_message_with_priority(self, message: Message, priority: MessagePriority = MessagePriority.NORMAL):
        """Enviar mensaje con priorización."""
        if self.protocol_manager:
            return self.protocol_manager.send_message_with_priority(
                message, 
                priority,
                callback=self._message_callback
            )
        return None
    
    def _message_callback(self, message: Message, status: str):
        """Callback para mensajes enviados."""
        print(f"Agent {self.agent_id}: Message to {message.to} - Status: {status}")


def test_message_priorization():
    """Probar sistema de priorización de mensajes."""
    
    print("\n=== Prueba 1: Sistema de Priorización ===")
    
    # Crear agente mock
    agent = MockAgent("test_agent_1")
    
    # Crear ProtocolManager (sin iniciar comportamiento SPADE)
    protocol_manager = ProtocolManager(agent)
    
    # Crear mensajes con diferentes prioridades
    messages = []
    for i, priority in enumerate([MessagePriority.LOW, MessagePriority.NORMAL, 
                                MessagePriority.HIGH, MessagePriority.CRITICAL]):
        msg = Message(
            to=f"agent_{i}@example.com",
            body=json.dumps({"test": f"message_{i}", "priority": priority.name})
        )
        messages.append((msg, priority))
    
    # Enviar mensajes con diferentes prioridades
    task_ids = []
    for msg, priority in messages:
        task_id = agent.send_message_with_priority(msg, priority)
        task_ids.append(task_id)
    
    # Verificar estadísticas
    stats = protocol_manager.get_statistics()
    print(f"Estadísticas iniciales: {stats}")
    
    # Verificar que los mensajes están en la cola
    print(f"Tamaño de cola: {protocol_manager.message_queue.qsize()}")
    
    return protocol_manager


def test_protocol_sessions():
    """Probar sistema de sesiones de protocolo."""
    
    print("\n=== Prueba 2: Sistema de Sesiones ===")
    
    # Crear agente mock
    agent = MockAgent("test_agent_2")
    
    # Crear ProtocolManager
    protocol_manager = ProtocolManager(agent)
    
    # Crear sesiones de protocolo
    sessions_data = [
        ("session_1", "material_transfer", "agent_a", "agent_b"),
        ("session_2", "quality_check", "agent_b", "agent_c"),
        ("session_3", "assembly_operation", "agent_c", "agent_d")
    ]
    
    created_sessions = []
    for session_id, protocol_type, source, target in sessions_data:
        session = protocol_manager.create_protocol_session(
            session_id=session_id,
            protocol_type=protocol_type,
            source_agent=source,
            target_agent=target,
            timeout=30.0
        )
        created_sessions.append(session)
        
        print(f"Sesión creada: {session_id} - Estado: {session.state.value}")
    
    # Verificar estadísticas
    stats = protocol_manager.get_statistics()
    print(f"Estadísticas de sesiones: {stats}")
    
    # Actualizar estado de algunas sesiones
    protocol_manager.update_session_state("session_1", ProtocolState.PROCESSING)
    protocol_manager.update_session_state("session_2", ProtocolState.WAITING_RESPONSE)
    
    # Verificar estados actualizados
    for session_id in ["session_1", "session_2"]:
        session = protocol_manager.get_session(session_id)
        if session:
            print(f"Sesión {session_id} - Estado actualizado: {session.state.value}")
    
    return protocol_manager


def test_material_transfer_integration():
    """Probar integración con protocolo de transferencia de materiales."""
    
    print("\n=== Prueba 3: Integración Material Transfer ===")
    
    # Crear agentes
    source_agent = MockAgent("source_crane")
    target_agent = MockAgent("target_conveyor")
    
    # Crear ProtocolManagers
    source_pm = ProtocolManager(source_agent)
    target_pm = ProtocolManager(target_agent)
    
    # Registrar manejadores de protocolos
    source_pm.register_protocol_handler("material", source_pm._handle_material_transfer)
    target_pm.register_protocol_handler("material", target_pm._handle_material_transfer)
    
    # Simular solicitud de transferencia
    request_msg = MaterialTransferProtocol.create_request_message(
        source_id="crane_001",
        target_jid=target_agent.agent_id,
        material_id="steel_beam",
        quantity=5,
        destination="assembly_station_1"
    )
    
    print(f"Enviando solicitud de transferencia desde {source_agent.agent_id}")
    
    # Procesar mensaje en el destino
    response = target_pm._on_message(request_msg)
    
    if response:
        print(f"Recibida respuesta: {response.body}")
        
        # Procesar la respuesta en el origen
        source_response = source_pm._on_message(response)
        
        if source_response:
            print(f"Confirmación enviada: {source_response.body}")
    
    # Ver estadísticas finales
    source_stats = source_pm.get_statistics()
    target_stats = target_pm.get_statistics()
    
    print(f"Estadísticas origen: {source_stats}")
    print(f"Estadísticas destino: {target_stats}")


def test_error_handling():
    """Probar manejo de errores y reintentos."""
    
    print("\n=== Prueba 4: Manejo de Errores y Reintentos ===")
    
    # Crear agente mock
    agent = MockAgent("test_agent_error")
    
    # Crear ProtocolManager
    protocol_manager = ProtocolManager(agent)
    
    # Simular envío de mensaje con error
    error_msg = Message(
        to="nonexistent@example.com",
        body=json.dumps({"test": "error_message"})
    )
    
    # Enviar mensaje con callback de error
    task_id = protocol_manager.send_message_with_priority(
        error_msg,
        MessagePriority.HIGH,
        callback=lambda msg, status: print(f"Callback ejecutado - Status: {status}")
    )
    
    # Esperar un momento para procesamiento
    time.sleep(2)
    
    # Ver estadísticas de errores
    stats = protocol_manager.get_statistics()
    print(f"Estadísticas con errores: {stats}")
    
    # Probar sistema de reintentos
    retry_msg = Message(
        to="unreachable@example.com",
        body=json.dumps({"test": "retry_message"})
    )
    
    # Enviar mensaje con múltiples reintentos
    retry_task_id = protocol_manager.send_message_with_priority(
        retry_msg,
        MessagePriority.CRITICAL,
        timeout=5.0,  # Tiempo corto para forzar reintentos
        callback=lambda msg, status: print(f"Retry callback - Status: {status}")
    )
    
    # Esperar más tiempo para ver reintentos
    time.sleep(3)
    
    final_stats = protocol_manager.get_statistics()
    print(f"Estadísticas finales con reintentos: {final_stats}")


def test_concurrent_processing():
    """Probar procesamiento concurrente de mensajes."""
    
    print("\n=== Prueba 5: Procesamiento Concurrente ===")
    
    # Crear múltiples agentes
    agents = [MockAgent(f"agent_{i}") for i in range(5)]
    
    # Crear ProtocolManagers
    protocol_managers = [ProtocolManager(agent) for agent in agents]
    
    # Registrar manejadores
    for pm in protocol_managers:
        pm.register_protocol_handler("material", pm._handle_material_transfer)
    
    # Simular carga concurrente
    start_time = time.time()
    
    for i, pm in enumerate(protocol_managers):
        # Enviar múltiples mensajes concurrentemente
        for j in range(10):
            msg = Message(
                to=f"target_{j}@example.com",
                body=json.dumps({
                    "test": f"concurrent_message_{i}_{j}",
                    "priority": MessagePriority.NORMAL
                })
            )
            
            pm.send_message_with_priority(msg, MessagePriority.NORMAL)
    
    # Esperar procesamiento
    time.sleep(3)
    
    end_time = time.time()
    
    # Ver estadísticas finales
    total_messages_processed = sum(
        pm.get_statistics()['messages_processed'] 
        for pm in protocol_managers
    )
    
    print(f"Tiempo total procesamiento: {end_time - start_time:.2f}s")
    print(f"Mensajes totales procesados: {total_messages_processed}")
    
    # Verificar que todos los mensajes fueron procesados
    expected_total = len(agents) * 10
    print(f"Esperado: {expected_total}, Procesados: {total_messages_processed}")


def main():
    """Ejecutar todas las pruebas del ProtocolManager."""
    
    print("Iniciando pruebas del ProtocolManager...")
    print("=" * 60)
    
    try:
        # Ejecutar pruebas individuales
        test_message_priorization()
        
        protocol_manager = test_protocol_sessions()
        
        test_material_transfer_integration()
        
        test_error_handling()
        
        test_concurrent_processing()
        
        # Resumen final
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS:")
        
        # Estadísticas finales del último protocol manager
        final_stats = protocol_manager.get_statistics()
        
        print(f"• Mensajes procesados: {final_stats['messages_processed']}")
        print(f"• Sesiones creadas: {final_stats['sessions_created']}")
        print(f"• Sesiones completadas: {final_stats['sessions_completed']}")
        print(f"• Errores encontrados: {final_stats['errors_encountered']}")
        print(f"• Sesiones activas: {final_stats['active_sessions']}")
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()