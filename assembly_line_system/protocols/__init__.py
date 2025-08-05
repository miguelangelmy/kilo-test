"""
Protocolos de comunicación para el sistema de línea de ensamblaje.

Este módulo contiene todos los protocolos y gestores de comunicación
para coordinar agentes en el entorno multiagente.
"""

from .material_transfer import MaterialTransferProtocol
from .protocol_manager import ProtocolManager
from .error_handler import (
    ErrorHandler,
    PriorityManager,
    ErrorSeverity,
    ErrorType,
    ErrorAction,
    create_default_error_handler,
    create_default_priority_manager
)

__all__ = [
    'MaterialTransferProtocol',
    'ProtocolManager',
    'ErrorHandler',
    'PriorityManager',
    'ErrorSeverity',
    'ErrorType',
    'ErrorAction',
    'create_default_error_handler',
    'create_default_priority_manager'
]
