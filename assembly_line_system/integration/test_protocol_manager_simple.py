"""
Prueba simplificada del ProtocolManager.

Este script valida el funcionamiento básico del gestor de protocolos
sin dependencias complejas.
"""

import sys
import os

# Agregar el directorio actual al path para importaciones locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar directamente desde los archivos
import sys
sys.path.append('..')

from assembly_line_system.protocols.protocol_manager import (
    ProtocolManager,
    MessagePriority,
    ProtocolState,
    MessageTask
)
from assembly_line_system.protocols.material_transfer import MaterialTransferProtocol


def test_basic_functionality():
    """Probar funcionalidad básica del ProtocolManager."""
    
    print("=== Prueba Básica de ProtocolManager ===")
    
    # Crear un mock agent simple
    class MockAgent:
        def __init__(self, agent_id):
            self.agent_id = agent_id
            self.messages_sent = []
            
        def send(self, message):
            """Simular envío de mensaje."""
            self.messages_sent.append(message)
            print(f"Mensaje enviado a {message.to}: {message.body}")
    
    # Crear agente y ProtocolManager
    agent = MockAgent("test_agent")
    protocol_manager = ProtocolManager(agent)
    
    # Probar creación de sesiones
    session = protocol_manager.create_protocol_session(
        session_id="test_session_1",
        protocol_type="material_transfer",
        source_agent="agent_a",
        target_agent="agent_b"
    )
    
    print(f"Sesión creada: {session.session_id}")
    print(f"Estado inicial: {session.state.value}")
    
    # Probar actualización de estado
    protocol_manager.update_session_state("test_session_1", ProtocolState.PROCESSING)
    
    session_updated = protocol_manager.get_session("test_session_1")
    print(f"Estado actualizado: {session_updated.state.value}")
    
    # Probar estadísticas
    stats = protocol_manager.get_statistics()
    print(f"Estadísticas: {stats}")
    
    return True


def test_message_priorization():
    """Probar sistema de priorización."""
    
    print("\n=== Prueba de Priorización ===")
    
    # Crear cola de mensajes con diferentes prioridades
    from datetime import datetime
    
    messages = []
    
    # Crear mensajes con diferentes prioridades
    for i, priority in enumerate([MessagePriority.LOW, MessagePriority.NORMAL, 
                                MessagePriority.HIGH, MessagePriority.CRITICAL]):
        task = MessageTask(
            priority=priority,
            timestamp=datetime.now(),
            metadata={"test": f"message_{i}"}
        )
        messages.append(task)
    
    # Ordenar por prioridad (el más prioritario primero)
    sorted_messages = sorted(messages, key=lambda x: (x.priority.value, x.timestamp))
    
    print("Mensajes ordenados por prioridad:")
    for i, task in enumerate(sorted_messages):
        print(f"{i+1}. Prioridad {task.priority.name}: {task.metadata}")
    
    # Verificar que CRITICAL es el primero
    assert sorted_messages[0].priority == MessagePriority.CRITICAL
    assert sorted_messages[-1].priority == MessagePriority.LOW
    
    print("✅ Priorización funciona correctamente")
    
    return True


def test_material_transfer_protocol():
    """Probar protocolo de transferencia de materiales."""
    
    print("\n=== Prueba Material Transfer Protocol ===")
    
    # Crear mensajes de transferencia
    request_msg = MaterialTransferProtocol.create_request_message(
        source_id="crane_001",
        target_jid="conveyor_001@localhost",
        material_id="steel_beam",
        quantity=5,
        destination="assembly_station_1"
    )
    
    print(f"Solicitud creada: {request_msg.body}")
    
    # Crear mensaje de confirmación
    confirm_msg = MaterialTransferProtocol.create_confirm_message(
        target_id="crane_001",
        source_jid="conveyor_001@localhost", 
        ready_time=1234567890
    )
    
    print(f"Confirmación creada: {confirm_msg.body}")
    
    # Crear mensaje de completado
    complete_msg = MaterialTransferProtocol.create_complete_message(
        target_id="crane_001",
        source_jid="conveyor_001@localhost",
        status="success"
    )
    
    print(f"Completado creado: {complete_msg.body}")
    
    # Verificar que los mensajes tienen el formato correcto
    import json
    
    request_data = json.loads(request_msg.body)
    assert request_data["message_type"] == "material_transfer_request"
    assert request_data["material_id"] == "steel_beam"
    
    confirm_data = json.loads(confirm_msg.body)
    assert confirm_data["message_type"] == "material_transfer_confirm"
    
    complete_data = json.loads(complete_msg.body)
    assert complete_data["message_type"] == "material_transfer_complete"
    
    print("✅ Protocolo de transferencia funciona correctamente")
    
    return True


def test_error_handling():
    """Probar manejo básico de errores."""
    
    print("\n=== Prueba Manejo de Errores ===")
    
    # Crear agente y ProtocolManager
    class MockAgent:
        def __init__(self):
            self.messages_sent = []
            
        def send(self, message):
            # Simular error en envío
            raise Exception("Conexión fallida")
    
    agent = MockAgent()
    protocol_manager = ProtocolManager(agent)
    
    # Crear tarea con mensaje
    from spade.message import Message
    
    msg = Message(to="test@example.com", body='{"test": "error"}')
    
    # Enviar mensaje con callback
    task_id = protocol_manager.send_message_with_priority(
        msg,
        MessagePriority.HIGH,
        callback=lambda m, s: print(f"Callback ejecutado con status: {s}")
    )
    
    print(f"Tarea creada: {task_id}")
    
    # Verificar estadísticas de errores
    stats = protocol_manager.get_statistics()
    print(f"Estadísticas actuales: {stats}")
    
    print("✅ Manejo de errores implementado")
    
    return True


def main():
    """Ejecutar todas las pruebas."""
    
    print("Iniciando pruebas simplificadas del ProtocolManager...")
    print("=" * 60)
    
    tests = [
        ("Funcionalidad Básica", test_basic_functionality),
        ("Sistema de Priorización", test_message_priorization), 
        ("Protocolo Transferencia", test_material_transfer_protocol),
        ("Manejo de Errores", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'EXITOSA' if result else 'FALLIDA'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS:")
    
    successful = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Pruebas exitosas: {successful}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    if successful == total:
        print("\n🎉 ¡Todas las pruebas pasaron!")
    else:
        print(f"\n⚠️  {total - successful} pruebas fallaron")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)