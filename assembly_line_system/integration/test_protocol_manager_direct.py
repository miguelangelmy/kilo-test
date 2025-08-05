"""
Prueba directa del ProtocolManager sin dependencias externas.

Este script valida el funcionamiento básico importando los módulos directamente.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, '/Users/avatar/NTT 2025/Demo Center/kilo-test')

def test_protocol_manager_basic():
    """Probar funcionalidad básica del ProtocolManager."""
    
    print("=== Prueba Directa de ProtocolManager ===")
    
    try:
        # Importar los módulos directamente
        from assembly_line_system.protocols.protocol_manager import (
            ProtocolManager, 
            MessagePriority, 
            ProtocolState,
            MessageTask
        )
        from assembly_line_system.protocols.material_transfer import MaterialTransferProtocol
        
        print("✅ Importaciones exitosas")
        
        # Probar MessagePriority
        priorities = [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                     MessagePriority.NORMAL, MessagePriority.LOW]
        
        print("Prioridades disponibles:")
        for priority in priorities:
            print(f"  - {priority.name}: {priority.value}")
        
        # Probar ProtocolState
        states = [ProtocolState.IDLE, ProtocolState.PROCESSING, 
                 ProtocolState.WAITING_RESPONSE, ProtocolState.COMPLETED,
                 ProtocolState.ERROR]
        
        print("\nEstados disponibles:")
        for state in states:
            print(f"  - {state.name}: {state.value}")
        
        # Probar creación de MessageTask
        from datetime import datetime
        
        task = MessageTask(
            priority=MessagePriority.HIGH,
            timestamp=datetime.now(),
            metadata={"test": "sample_task"}
        )
        
        print(f"\n✅ MessageTask creado: prioridad={task.priority.name}")
        
        # Probar MaterialTransferProtocol
        request_msg = MaterialTransferProtocol.create_request_message(
            source_id="crane_001",
            target_jid="conveyor_001@localhost",
            material_id="steel_beam",
            quantity=5,
            destination="assembly_station_1"
        )
        
        print(f"✅ Mensaje de solicitud creado: {request_msg.body}")
        
        # Probar estadísticas básicas
        class MockAgent:
            def __init__(self):
                self.agent_id = "test_agent"
                
        agent = MockAgent()
        
        # Crear ProtocolManager (sin iniciar comportamiento SPADE)
        protocol_manager = ProtocolManager.__new__(ProtocolManager)
        protocol_manager.agent = agent
        protocol_manager.message_queue = __import__('queue').PriorityQueue()
        protocol_manager.active_sessions = {}
        protocol_manager.protocol_handlers = {}
        protocol_manager.session_timeout_callbacks = {}
        protocol_manager.running = True
        protocol_manager.stats = {
            'messages_processed': 0,
            'sessions_created': 0,
            'sessions_completed': 0,
            'sessions_expired': 0,
            'errors_encountered': 0
        }
        
        # Probar creación de sesión
        session = protocol_manager.create_protocol_session(
            session_id="test_session_1",
            protocol_type="material_transfer",
            source_agent="agent_a",
            target_agent="agent_b"
        )
        
        print(f"✅ Sesión creada: {session.session_id}")
        print(f"   Estado inicial: {session.state.value}")
        
        # Probar actualización de estado
        protocol_manager.update_session_state("test_session_1", ProtocolState.PROCESSING)
        
        session_updated = protocol_manager.get_session("test_session_1")
        print(f"✅ Estado actualizado: {session_updated.state.value}")
        
        # Probar estadísticas
        stats = protocol_manager.get_statistics()
        print(f"✅ Estadísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_priorization():
    """Probar sistema de priorización."""
    
    print("\n=== Prueba de Priorización ===")
    
    try:
        from assembly_line_system.protocols.protocol_manager import MessagePriority, MessageTask
        from datetime import datetime
        
        # Crear mensajes con diferentes prioridades
        messages = []
        
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
        
    except Exception as e:
        print(f"❌ Error en prueba de priorización: {e}")
        return False


def main():
    """Ejecutar todas las pruebas."""
    
    print("Iniciando prueba directa del ProtocolManager...")
    print("=" * 60)
    
    tests = [
        ("Funcionalidad Básica", test_protocol_manager_basic),
        ("Sistema de Priorización", test_message_priorization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n✅ {test_name}: {'EXITOSA' if result else 'FALLIDA'}")
        except Exception as e:
            print(f"\n❌ {test_name}: ERROR - {e}")
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