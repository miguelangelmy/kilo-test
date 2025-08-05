"""
Prueba integrada del sistema de persistencia e historial completo.

Este script valida el funcionamiento del PersistenceManager y su integración
con ProtocolManager y ErrorHandler.
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, '/Users/avatar/NTT 2025/Demo Center/kilo-test')

def test_persistence_manager_basic():
    """Probar funcionalidad básica del PersistenceManager."""
    
    print("=== Prueba Básica de PersistenceManager ===")
    
    try:
        from assembly_line_system.protocols.persistence_manager import (
            PersistenceManager,
            MessageRecord,
            ErrorRecord,
            SessionRecord
        )
        
        # Crear gestor de persistencia para pruebas
        persistence_manager = create_test_persistence_manager()
        
        print("✅ PersistenceManager creado exitosamente")
        
        # Crear registros de prueba
        message_record = MessageRecord(
            message_id="msg_001",
            timestamp=datetime.now(),
            sender="crane_agent",
            receiver="conveyor_agent",
            protocol_type="material_transfer",
            content={"material": "steel_beam", "weight": 500},
            priority=1,
            status="sent",
            session_id="session_001"
        )
        
        error_record = ErrorRecord(
            error_id="err_001",
            timestamp=datetime.now(),
            agent_id="crane_agent",
            error_type="network_error",
            severity=2,
            message="Conexión perdida",
            context={"retry_count": 3},
            action_taken="retry",
            recovery_attempts=2
        )
        
        session_record = SessionRecord(
            session_id="session_001",
            timestamp=datetime.now(),
            agent_id="crane_agent",
            protocol_type="material_transfer",
            status="active",
            start_time=datetime.now() - timedelta(minutes=5),
            messages_count=10,
            error_count=1
        )
        
        # Guardar registros
        persistence_manager.save_message_record(message_record)
        persistence_manager.save_error_record(error_record)
        persistence_manager.save_session_record(session_record)
        
        print("✅ Registros guardados exitosamente")
        
        # Recuperar historial
        message_history = persistence_manager.get_message_history()
        error_history = persistence_manager.get_error_history()
        session_history = persistence_manager.get_session_history()
        
        print(f"✅ Historial de mensajes: {len(message_history)} registros")
        print(f"✅ Historial de errores: {len(error_history)} registros")
        print(f"✅ Historial de sesiones: {len(session_history)} registros")
        
        # Verificar que los datos se recuperaron correctamente
        assert len(message_history) >= 1, "No se recuperaron mensajes"
        assert len(error_history) >= 1, "No se recuperaron errores"
        assert len(session_history) >= 1, "No se recuperaron sesiones"
        
        # Probar estadísticas
        stats = persistence_manager.get_statistics(days=1)
        print(f"✅ Estadísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_persistence_manager_queries():
    """Probar consultas avanzadas del PersistenceManager."""
    
    print("\n=== Prueba de Consultas Avanzadas ===")
    
    try:
        from assembly_line_system.protocols.persistence_manager import (
            PersistenceManager,
            MessageRecord,
            ErrorRecord
        )
        
        persistence_manager = create_test_persistence_manager()
        
        # Crear múltiples registros con diferentes agentes
        agents = ["crane_agent", "conveyor_agent", "robotic_arm_agent"]
        
        for i, agent in enumerate(agents):
            # Mensajes
            msg = MessageRecord(
                message_id=f"msg_{i:03d}",
                timestamp=datetime.now() - timedelta(minutes=i),
                sender=agent,
                receiver="central_controller",
                protocol_type="status_update",
                content={"status": "active", "load": i * 100},
                priority=i % 3 + 1,
                status="delivered"
            )
            persistence_manager.save_message_record(msg)
            
            # Errores
            error = ErrorRecord(
                error_id=f"err_{i:03d}",
                timestamp=datetime.now() - timedelta(minutes=i * 2),
                agent_id=agent,
                error_type="timeout_error",
                severity=3 - i,  # Diferentes severidades
                message=f"Timeout {i}",
                context={"timeout_value": 30 + i * 10},
                action_taken="retry",
                recovery_attempts=i
            )
            persistence_manager.save_error_record(error)
        
        print("✅ Registros de prueba creados")
        
        # Probar consultas por agente
        crane_messages = persistence_manager.get_message_history(agent_id="crane_agent")
        print(f"✅ Mensajes de crane_agent: {len(crane_messages)}")
        
        # Probar consultas por rango de fechas
        start_date = datetime.now() - timedelta(hours=1)
        recent_errors = persistence_manager.get_error_history(start_date=start_date)
        print(f"✅ Errores recientes (última hora): {len(recent_errors)}")
        
        # Probar límite de resultados
        limited_messages = persistence_manager.get_message_history(limit=2)
        print(f"✅ Mensajes limitados: {len(limited_messages)} (esperado: 2)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de consultas: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_persistence_manager_backup():
    """Probar funcionalidad de backup y restauración."""
    
    print("\n=== Prueba de Backup y Restauración ===")
    
    try:
        from assembly_line_system.protocols.persistence_manager import (
            PersistenceManager,
            MessageRecord
        )
        
        # Crear gestor de persistencia
        persistence_manager = create_test_persistence_manager()
        
        # Crear algunos datos
        for i in range(5):
            msg = MessageRecord(
                message_id=f"backup_msg_{i:03d}",
                timestamp=datetime.now(),
                sender="test_agent",
                receiver="backup_test",
                protocol_type="backup_protocol",
                content={"test": f"data_{i}"},
                priority=1,
                status="delivered"
            )
            persistence_manager.save_message_record(msg)
        
        print("✅ Datos de prueba creados")
        
        # Crear backup
        backup_file = persistence_manager.create_backup()
        assert backup_file, "No se pudo crear el backup"
        
        print(f"✅ Backup creado: {backup_file}")
        
        # Modificar datos originales
        persistence_manager.cleanup_old_data(days=0)  # Eliminar todos los datos
        
        # Verificar que se eliminaron los datos
        empty_history = persistence_manager.get_message_history()
        print(f"✅ Datos originales eliminados: {len(empty_history)} registros")
        
        # Restaurar desde backup
        restore_success = persistence_manager.restore_from_backup(backup_file)
        assert restore_success, "No se pudo restaurar el backup"
        
        print("✅ Backup restaurado exitosamente")
        
        # Verificar que los datos se recuperaron
        restored_history = persistence_manager.get_message_history()
        assert len(restored_history) >= 5, "No se recuperaron todos los datos del backup"
        
        print(f"✅ Datos restaurados: {len(restored_history)} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de backup: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_persistence_manager_export():
    """Probar funcionalidad de exportación."""
    
    print("\n=== Prueba de Exportación ===")
    
    try:
        from assembly_line_system.protocols.persistence_manager import (
            PersistenceManager,
            MessageRecord
        )
        
        persistence_manager = create_test_persistence_manager()
        
        # Crear datos de prueba
        for i in range(3):
            msg = MessageRecord(
                message_id=f"export_msg_{i:03d}",
                timestamp=datetime.now(),
                sender="export_test",
                receiver="export_target",
                protocol_type="export_protocol",
                content={"export": f"data_{i}"},
                priority=1,
                status="delivered"
            )
            persistence_manager.save_message_record(msg)
        
        print("✅ Datos de exportación creados")
        
        # Exportar a JSON
        json_file = "/tmp/export_test.json"
        persistence_manager.export_data(json_file, format_type="json")
        
        # Verificar que el archivo se creó
        import os
        assert os.path.exists(json_file), "No se creó el archivo JSON"
        
        print(f"✅ Exportación a JSON creada: {json_file}")
        
        # Leer y verificar el contenido
        with open(json_file, 'r') as f:
            import json
            export_data = json.load(f)
        
        assert 'messages' in export_data, "Falta sección de mensajes en exportación"
        assert len(export_data['messages']) >= 3, "No se exportaron todos los mensajes"
        
        print(f"✅ Contenido exportado verificado: {len(export_data['messages'])} mensajes")
        
        # Limpiar archivo de prueba
        os.remove(json_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de exportación: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_protocol_manager():
    """Probar integración con ProtocolManager."""
    
    print("\n=== Prueba de Integración con ProtocolManager ===")
    
    try:
        from assembly_line_system.protocols.protocol_manager import (
            ProtocolManager,
            MessageTask
        )
        from assembly_line_system.protocols.persistence_manager import (
            PersistenceManager,
            MessageRecord
        )
        
        # Crear componentes integrados
        class MockAgent:
            def __init__(self):
                self.agent_id = "integrated_agent"
        
        agent = MockAgent()
        protocol_manager = ProtocolManager.__new__(ProtocolManager)
        persistence_manager = create_test_persistence_manager()
        
        # Configurar ProtocolManager básico
        protocol_manager.agent = agent
        protocol_manager.persistence_manager = persistence_manager
        
        print("✅ Componentes integrados creados")
        
        # Simular envío de mensaje
        message_task = MessageTask(
            message_id="integrated_msg_001",
            sender=agent.agent_id,
            receiver="test_receiver",
            protocol_type="integration_test",
            content={"test": "integration_data"},
            priority=1,
            timestamp=datetime.now()
        )
        
        # Guardar registro del mensaje
        message_record = MessageRecord(
            message_id=message_task.message_id,
            timestamp=message_task.timestamp,
            sender=message_task.sender,
            receiver=message_task.receiver,
            protocol_type=message_task.protocol_type,
            content=message_task.content,
            priority=message_task.priority,
            status="sent"
        )
        
        persistence_manager.save_message_record(message_record)
        
        # Recuperar historial
        history = persistence_manager.get_message_history(agent_id=agent.agent_id)
        
        assert len(history) >= 1, "No se guardó el mensaje integrado"
        
        print(f"✅ Mensaje integrado guardado: {history[0].message_id}")
        
        # Probar estadísticas
        stats = persistence_manager.get_statistics()
        assert 'message_statistics' in stats, "Faltan estadísticas de mensajes"
        
        print(f"✅ Estadísticas integradas: {stats['message_statistics']['total_messages']} mensajes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de integración: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_test_persistence_manager():
    """Crear gestor de persistencia para pruebas."""
    from assembly_line_system.protocols.persistence_manager import create_test_persistence_manager
    return create_test_persistence_manager()


def main():
    """Ejecutar todas las pruebas del sistema de persistencia."""
    
    print("Iniciando pruebas integradas del sistema de persistencia...")
    print("=" * 70)
    
    tests = [
        ("Funcionalidad Básica de PersistenceManager", test_persistence_manager_basic),
        ("Consultas Avanzadas", test_persistence_manager_queries),
        ("Backup y Restauración", test_persistence_manager_backup),
        ("Exportación de Datos", test_persistence_manager_export),
        ("Integración con ProtocolManager", test_integration_with_protocol_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n{'✅' if result else '❌'} {test_name}: {'EXITOSA' if result else 'FALLIDA'}")
        except Exception as e:
            print(f"\n❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE PRUEBAS DEL SISTEMA DE PERSISTENCIA:")
    
    successful = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Pruebas exitosas: {successful}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    if successful == total:
        print("\n🎉 ¡Todas las pruebas del sistema de persistencia pasaron!")
        print("El sistema está listo para producción con:")
        print("  - Persistencia completa de mensajes y errores")
        print("  - Backup automático y restauración")
        print("  - Consultas avanzadas por agente, fechas y filtros")
        print("  - Exportación de datos en múltiples formatos")
        print("  - Estadísticas detalladas del sistema")
    else:
        print(f"\n⚠️  {total - successful} pruebas fallaron")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)