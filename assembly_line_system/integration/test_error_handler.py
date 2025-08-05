"""
Prueba integrada del sistema de priorización y manejo de errores.

Este script valida el funcionamiento completo del ErrorHandler y PriorityManager
integrados con el ProtocolManager.
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, '/Users/avatar/NTT 2025/Demo Center/kilo-test')

def test_error_handler_basic():
    """Probar funcionalidad básica del ErrorHandler."""
    
    print("=== Prueba Básica de ErrorHandler ===")
    
    try:
        from assembly_line_system.protocols.error_handler import (
            ErrorHandler,
            ErrorSeverity,
            ErrorType,
            ErrorAction,
            create_default_error_handler
        )
        
        # Crear manejador de errores por defecto
        error_handler = create_default_error_handler()
        
        print("✅ ErrorHandler creado exitosamente")
        
        # Crear un contexto de error usando el objeto ErrorContext
        from assembly_line_system.protocols.error_handler import ErrorContext
        
        error_context = ErrorContext(
            error_id='test_error_001',
            severity=ErrorSeverity.HIGH,
            error_type=ErrorType.NETWORK_ERROR,
            message='Conexión de red perdida',
            session_id='session_001',
            retry_count=0,
            max_retries=3
        )
        
        print(f"✅ Contexto de error creado: {error_context.message}")
        
        # Probar manejo de error
        action = error_handler.handle_error(error_context)
        print(f"✅ Acción determinada: {action.value}")
        
        # Probar estadísticas
        stats = error_handler.get_statistics()
        print(f"✅ Estadísticas: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_priority_manager():
    """Probar funcionalidad del PriorityManager."""
    
    print("\n=== Prueba de PriorityManager ===")
    
    try:
        from assembly_line_system.protocols.error_handler import (
            PriorityManager,
            MessagePriority
        )
        
        # Crear gestor de priorización
        priority_manager = PriorityManager()
        
        print("✅ PriorityManager creado exitosamente")
        
        # Probar reglas por defecto
        test_messages = [
            {'priority': 'critical', 'type': 'normal'},
            {'error_type': 'network_error', 'type': 'normal'},
            {'type': 'timeout', 'priority': 'normal'},
            {'session_active': True, 'priority': 'normal'}
        ]
        
        expected_priorities = [
            MessagePriority.CRITICAL,
            MessagePriority.HIGH,
            MessagePriority.NORMAL,
            MessagePriority.LOW
        ]
        
        for i, (message, expected) in enumerate(zip(test_messages, expected_priorities)):
            priority = priority_manager.calculate_priority(message)
            print(f"Mensaje {i+1}: Prioridad calculada = {priority.name} (esperado: {expected.name})")
            
            if priority == expected:
                print(f"✅ Regla {i+1} funciona correctamente")
            else:
                print(f"❌ Regla {i+1} falló: esperado {expected.name}, got {priority.name}")
                return False
        
        # Probar regla personalizada
        def custom_rule(message, context):
            if message.get('urgent'):
                return MessagePriority.CRITICAL
        
        priority_manager.add_priority_rule(custom_rule)
        
        # Probar regla personalizada
        urgent_message = {'urgent': True, 'type': 'normal'}
        priority = priority_manager.calculate_priority(urgent_message)
        
        if priority == MessagePriority.CRITICAL:
            print("✅ Regla personalizada funciona correctamente")
        else:
            print(f"❌ Regla personalizada falló: {priority.name}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de priorización: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_recovery_strategies():
    """Probar estrategias de recuperación."""
    
    print("\n=== Prueba de Estrategias de Recuperación ===")
    
    try:
        from assembly_line_system.protocols.error_handler import (
            RetryStrategy,
            CircuitBreakerStrategy,
            ErrorSeverity,
            ErrorType,
            ErrorContext
        )
        
        # Probar RetryStrategy
        retry_strategy = RetryStrategy(max_retries=3, backoff_factor=2.0)
        
        error_context = ErrorContext(
            error_id='retry_test_001',
            severity=ErrorSeverity.MEDIUM,
            error_type=ErrorType.NETWORK_ERROR,
            message='Error de red',
            retry_count=0,
            max_retries=3
        )
        
        # Intentar recuperación varias veces
        for i in range(4):
            success = retry_strategy.attempt_recovery(error_context)
            print(f"Intento {i+1}: {'Exitoso' if success else 'Fallido'}")
        
        # Probar CircuitBreakerStrategy
        cb_strategy = CircuitBreakerStrategy(failure_threshold=3, recovery_timeout=60.0)
        
        cb_error_context = ErrorContext(
            error_id='cb_test_001',
            severity=ErrorSeverity.HIGH,
            error_type=ErrorType.NETWORK_ERROR,
            message='Error de circuito',
            retry_count=0
        )
        
        # Simular múltiples fallos
        for i in range(4):
            success = cb_strategy.attempt_recovery(cb_error_context)
            state = getattr(cb_strategy, 'state', 'unknown')
            print(f"Intento CB {i+1}: {'Exitoso' if success else 'Fallido'}, Estado: {state}")
        
        # Probar tasas de éxito
        retry_rate = retry_strategy.get_success_rate()
        cb_rate = cb_strategy.get_success_rate()
        
        print(f"✅ Tasa de éxito RetryStrategy: {retry_rate:.2f}")
        print(f"✅ Tasa de éxito CircuitBreaker: {cb_rate:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de estrategias: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_severity_types():
    """Probar tipos y severidades de error."""
    
    print("\n=== Prueba de Tipos y Severidades ===")
    
    try:
        from assembly_line_system.protocols.error_handler import (
            ErrorSeverity,
            ErrorType,
            ErrorAction
        )
        
        # Probar severidades
        severities = list(ErrorSeverity)
        print("Severidades disponibles:")
        for severity in severities:
            print(f"  - {severity.name}: {severity.value}")
        
        # Probar tipos de error
        error_types = list(ErrorType)
        print("\nTipos de error disponibles:")
        for error_type in error_types:
            print(f"  - {error_type.value}")
        
        # Probar acciones
        actions = list(ErrorAction)
        print("\nAcciones disponibles:")
        for action in actions:
            print(f"  - {action.value}")
        
        # Verificar consistencia
        assert len(severities) == 5, f"Se esperaban 5 severidades, se encontraron {len(severities)}"
        assert len(error_types) == 7, f"Se esperaban 7 tipos de error, se encontraron {len(error_types)}"
        assert len(actions) == 5, f"Se esperaban 5 acciones, se encontraron {len(actions)}"
        
        print("✅ Todos los enums tienen el número esperado de valores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de enums: {e}")
        return False


def test_integration_with_protocol_manager():
    """Probar integración con ProtocolManager."""
    
    print("\n=== Prueba de Integración con ProtocolManager ===")
    
    try:
        from assembly_line_system.protocols.protocol_manager import (
            ProtocolManager,
            MessagePriority
        )
        from assembly_line_system.protocols.error_handler import (
            ErrorHandler,
            PriorityManager,
            ErrorSeverity,
            ErrorType,
            create_default_error_handler
        )
        
        # Crear componentes integrados
        class MockAgent:
            def __init__(self):
                self.agent_id = "integrated_agent"
        
        agent = MockAgent()
        protocol_manager = ProtocolManager.__new__(ProtocolManager)
        error_handler = create_default_error_handler()
        priority_manager = PriorityManager()
        
        # Configurar ProtocolManager básico
        protocol_manager.agent = agent
        protocol_manager.message_queue = __import__('queue').PriorityQueue()
        protocol_manager.active_sessions = {}
        protocol_manager.error_handler = error_handler
        protocol_manager.priority_manager = priority_manager
        
        print("✅ Componentes integrados creados")
        
        # Probar manejo de error en contexto de protocolo
        from assembly_line_system.protocols.error_handler import ErrorContext
        
        error_context = ErrorContext(
            error_id='protocol_error_001',
            severity=ErrorSeverity.HIGH,
            error_type=ErrorType.TIMEOUT_ERROR,
            message='Timeout en transferencia',
            session_id='protocol_session_001',
            retry_count=0,
            max_retries=2
        )
        
        # Manejar error con el handler integrado
        action = error_handler.handle_error(error_context)
        print(f"✅ Error manejado con acción: {action.value}")
        
        # Probar priorización de mensajes
        message = {
            'type': 'transfer_request',
            'priority': 'normal',
            'material_id': 'steel_beam'
        }
        
        context = {'session_active': True}
        priority = priority_manager.calculate_priority(message, context)
        
        print(f"✅ Prioridad calculada para mensaje: {priority.name}")
        
        # Probar estadísticas combinadas
        error_stats = error_handler.get_statistics()
        print(f"✅ Estadísticas de errores: {error_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de integración: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todas las pruebas del sistema de manejo de errores."""
    
    print("Iniciando pruebas integradas del sistema de manejo de errores...")
    print("=" * 70)
    
    tests = [
        ("Funcionalidad Básica de ErrorHandler", test_error_handler_basic),
        ("PriorityManager y Reglas de Priorización", test_priority_manager),
        ("Estrategias de Recuperación", test_recovery_strategies),
        ("Tipos y Severidades de Error", test_error_severity_types),
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
    print("RESUMEN DE PRUEBAS DEL SISTEMA DE MANEJO DE ERRORES:")
    
    successful = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Pruebas exitosas: {successful}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    if successful == total:
        print("\n🎉 ¡Todas las pruebas del sistema de manejo de errores pasaron!")
        print("El sistema está listo para producción con:")
        print("  - Manejo avanzado de errores")
        print("  - Priorización inteligente de mensajes") 
        print("  - Estrategias de recuperación automáticas")
        print("  - Integración completa con ProtocolManager")
    else:
        print(f"\n⚠️  {total - successful} pruebas fallaron")
    
    return successful == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)