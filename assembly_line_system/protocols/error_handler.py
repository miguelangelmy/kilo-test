"""
Sistema avanzado de manejo de errores y priorización.

Este módulo implementa un sistema robusto para manejar errores en la comunicación
entre agentes, con mecanismos de reintento, priorización inteligente y recuperación.
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
import threading
from queue import PriorityQueue, Empty

# Importar MessagePriority desde protocol_manager
try:
    from .protocol_manager import MessagePriority, ProtocolState
except ImportError:
    # Fallback para evitar errores de importación circular
    class MessagePriority(Enum):
        CRITICAL = 1
        HIGH = 2
        NORMAL = 3
        LOW = 4
        BACKGROUND = 5

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Gravedad de los errores."""
    CRITICAL = 1      # Errores críticos que detienen el sistema
    HIGH = 2          # Errores graves que requieren atención inmediata  
    MEDIUM = 3        # Errores moderados que afectan el rendimiento
    LOW = 4           # Errores leves que pueden esperar
    INFO = 5          # Información de diagnóstico


class ErrorType(Enum):
    """Tipos de errores en el sistema."""
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    PROTOCOL_ERROR = "protocol_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorAction(Enum):
    """Acciones a tomar ante errores."""
    RETRY = "retry"
    SKIP = "skip"
    ESCALATE = "escalate"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"


@dataclass
class ErrorContext:
    """Contexto de un error."""
    
    error_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    error_type: ErrorType = ErrorType.UNKNOWN_ERROR
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    backoff_factor: float = 2.0
    next_retry_time: Optional[datetime] = None
    
    def can_retry(self) -> bool:
        """Verificar si se puede reintentar."""
        return self.retry_count < self.max_retries
    
    def calculate_next_retry(self) -> datetime:
        """Calcular próxima hora de reintento con backoff exponencial."""
        if not self.can_retry():
            return None
        
        # Backoff exponencial: base * (factor ^ retry_count)
        wait_time = self.backoff_factor ** self.retry_count
        next_retry = datetime.now() + timedelta(seconds=wait_time)
        
        self.next_retry_time = next_retry
        return next_retry
    
    def increment_retry(self):
        """Incrementar contador de reintentos."""
        self.retry_count += 1
        self.calculate_next_retry()


@dataclass 
class ErrorActionConfig:
    """Configuración de acciones para errores."""
    
    action: ErrorAction
    condition: Callable[[ErrorContext], bool] = lambda ctx: True
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def should_apply(self, error_context: ErrorContext) -> bool:
        """Verificar si la acción debe aplicarse."""
        return self.condition(error_context)


class ErrorRecoveryStrategy:
    """Estrategia de recuperación de errores."""
    
    def __init__(self, name: str):
        self.name = name
        self.success_count = 0
        self.failure_count = 0
    
    def attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Intentar recuperar del error."""
        raise NotImplementedError
    
    def get_success_rate(self) -> float:
        """Obtener tasa de éxito."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total


class RetryStrategy(ErrorRecoveryStrategy):
    """Estrategia de reintento."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        super().__init__("retry")
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Intentar reintento."""
        if not error_context.can_retry():
            return False
        
        error_context.increment_retry()
        
        # Simular reintento exitoso/fallido
        success = error_context.retry_count <= self.max_retries
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        return success


class CircuitBreakerStrategy(ErrorRecoveryStrategy):
    """Estrategia de circuit breaker."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        super().__init__("circuit_breaker")
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Intentar recuperación con circuit breaker."""
        current_time = datetime.now()
        
        # Verificar estado del circuito
        if self.state == "open":
            if (current_time - self.last_failure_time).total_seconds() > self.recovery_timeout:
                # Cambiar a half_open para probar
                self.state = "half_open"
            else:
                return False
        
        # Simular intento
        success = error_context.retry_count <= 2  # Lógica simplificada
        
        if not success:
            self.failure_count += 1
            self.last_failure_time = current_time
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
        else:
            # Éxito en half_open, cerrar circuito
            if self.state == "half_open":
                self.state = "closed"
            
            self.success_count += 1
            self.failure_count = 0
        
        return success


class ErrorHandler:
    """Manejador central de errores."""
    
    def __init__(self):
        self.error_queue = PriorityQueue()
        self.recovery_strategies: Dict[str, ErrorRecoveryStrategy] = {}
        self.error_configs: List[ErrorActionConfig] = []
        self.active_errors: Dict[str, ErrorContext] = {}
        
        # Hilos
        self.running = False
        self.processing_thread = None
        
        # Estadísticas
        self.total_errors = 0
        self.recovered_errors = 0
        self.escalated_errors = 0
        
    def register_recovery_strategy(self, strategy: ErrorRecoveryStrategy):
        """Registrar estrategia de recuperación."""
        self.recovery_strategies[strategy.name] = strategy
        logger.info(f"Registered recovery strategy: {strategy.name}")
    
    def add_error_config(self, config: ErrorActionConfig):
        """Añadir configuración de manejo de errores."""
        self.error_configs.append(config)
    
    def handle_error(self, error_context: ErrorContext) -> Optional[ErrorAction]:
        """Manejar un error."""
        
        # Registrar error
        self.total_errors += 1
        self.active_errors[error_context.error_id] = error_context
        
        logger.warning(f"Handling error {error_context.error_id}: "
                      f"{error_context.severity.name} - {error_context.message}")
        
        # Determinar acción a tomar
        action = self._determine_action(error_context)
        
        if action == ErrorAction.RETRY:
            return self._handle_retry(error_context)
        elif action == ErrorAction.ESCALATE:
            return self._handle_escalation(error_context)
        elif action == ErrorAction.CIRCUIT_BREAKER:
            return self._handle_circuit_breaker(error_context)
        else:
            logger.info(f"Error {error_context.error_id} handled with action: {action.value}")
            return action
    
    def _determine_action(self, error_context: ErrorContext) -> ErrorAction:
        """Determinar acción a tomar basada en configuración."""
        
        for config in self.error_configs:
            if config.should_apply(error_context):
                return config.action
        
        # Acción por defecto según severidad
        if error_context.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            return ErrorAction.ESCALATE
        elif error_context.severity == ErrorSeverity.MEDIUM:
            return ErrorAction.RETRY
        else:
            return ErrorAction.SKIP
    
    def _handle_retry(self, error_context: ErrorContext) -> Optional[ErrorAction]:
        """Manejar reintento."""
        
        retry_strategy = self.recovery_strategies.get("retry")
        if not retry_strategy:
            logger.error("No retry strategy available")
            return ErrorAction.SKIP
        
        success = retry_strategy.attempt_recovery(error_context)
        
        if success:
            logger.info(f"Retry scheduled for error {error_context.error_id}")
            return ErrorAction.RETRY
        else:
            logger.warning(f"Max retries exceeded for error {error_context.error_id}")
            return ErrorAction.ESCALATE
    
    def _handle_escalation(self, error_context: ErrorContext) -> Optional[ErrorAction]:
        """Manejar escalada de errores."""
        
        self.escalated_errors += 1
        
        # Aquí se podría implementar notificación, logging avanzado, etc.
        logger.error(f"ESCALATING error {error_context.error_id}: "
                    f"{error_context.severity.name} - {error_context.message}")
        
        # Actualizar estadísticas
        if error_context.session_id:
            session = self.active_errors.get(error_context.session_id)
            if session:
                session.retry_count += 1
        
        return ErrorAction.ESCALATE
    
    def _handle_circuit_breaker(self, error_context: ErrorContext) -> Optional[ErrorAction]:
        """Manejar circuit breaker."""
        
        cb_strategy = self.recovery_strategies.get("circuit_breaker")
        if not cb_strategy:
            logger.error("No circuit breaker strategy available")
            return ErrorAction.SKIP
        
        success = cb_strategy.attempt_recovery(error_context)
        
        if success:
            logger.info(f"Circuit breaker reset for error {error_context.error_id}")
            return ErrorAction.RETRY
        else:
            logger.warning(f"Circuit breaker open for error {error_context.error_id}")
            return ErrorAction.SKIP
    
    def process_error_queue(self):
        """Procesar cola de errores en hilo separado."""
        
        while self.running:
            try:
                # Obtener siguiente error (con timeout)
                error_context = self.error_queue.get(timeout=1.0)
                
                # Procesar error
                action = self.handle_error(error_context)
                
                if action == ErrorAction.RETRY and error_context.next_retry_time:
                    # Reagregar a cola para reintento
                    self.error_queue.put(error_context)
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing error queue: {e}")
    
    def start(self):
        """Iniciar manejador de errores."""
        
        self.running = True
        self.processing_thread = threading.Thread(target=self.process_error_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logger.info("Error handler started")
    
    def stop(self):
        """Detener manejador de errores."""
        
        self.running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        
        logger.info("Error handler stopped")
    
    def add_error_to_queue(self, error_context: ErrorContext):
        """Añadir error a la cola de procesamiento."""
        
        # Usar timestamp como prioridad (errores más recientes primero)
        priority = error_context.timestamp
        
        # Añadir a cola con priorización inversa (menor timestamp = mayor prioridad)
        self.error_queue.put((priority, error_context))
        
        logger.debug(f"Error {error_context.error_id} added to queue")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del manejador de errores."""
        
        total_strategies = len(self.recovery_strategies)
        
        strategy_stats = {}
        for name, strategy in self.recovery_strategies.items():
            strategy_stats[name] = {
                'success_rate': strategy.get_success_rate(),
                'success_count': strategy.success_count,
                'failure_count': strategy.failure_count
            }
        
        return {
            'total_errors': self.total_errors,
            'recovered_errors': self.recovered_errors,
            'escalated_errors': self.escalated_errors,
            'active_errors': len(self.active_errors),
            'queue_size': self.error_queue.qsize(),
            'total_strategies': total_strategies,
            'strategy_stats': strategy_stats
        }


class PriorityManager:
    """Gestor de priorización avanzado."""
    
    def __init__(self):
        self.priority_rules: List[Callable] = []
        self.default_priority = MessagePriority.NORMAL
        
    def add_priority_rule(self, rule: Callable):
        """Añadir regla de priorización."""
        self.priority_rules.append(rule)
    
    def calculate_priority(self, message: Dict[str, Any], 
                          context: Optional[Dict[str, Any]] = None) -> MessagePriority:
        """Calcular prioridad de mensaje basado en reglas."""
        
        context = context or {}
        
        # Aplicar reglas en orden
        for rule in self.priority_rules:
            try:
                priority = rule(message, context)
                if priority is not None:
                    return priority
            except Exception as e:
                logger.warning(f"Error applying priority rule: {e}")
        
        # Prioridad por defecto
        return self.default_priority
    
    def add_default_rules(self):
        """Añadir reglas de priorización por defecto."""
        
        # Regla 1: Mensajes críticos tienen máxima prioridad
        def critical_rule(message, context):
            if message.get('priority') == 'critical':
                return MessagePriority.CRITICAL
        self.add_priority_rule(critical_rule)
        
        # Regla 2: Errores de red tienen alta prioridad
        def network_error_rule(message, context):
            if message.get('error_type') == 'network_error':
                return MessagePriority.HIGH
        self.add_priority_rule(network_error_rule)
        
        # Regla 3: Mensajes de timeout tienen prioridad media
        def timeout_rule(message, context):
            if message.get('type') == 'timeout':
                return MessagePriority.NORMAL
        self.add_priority_rule(timeout_rule)
        
        # Regla 4: Mensajes de sesión activa tienen prioridad baja
        def active_session_rule(message, context):
            if context.get('session_active'):
                return MessagePriority.LOW
        self.add_priority_rule(active_session_rule)


def create_default_error_handler() -> ErrorHandler:
    """Crear manejador de errores con configuración por defecto."""
    
    handler = ErrorHandler()
    
    # Registrar estrategias de recuperación
    retry_strategy = RetryStrategy(max_retries=3, backoff_factor=2.0)
    circuit_breaker = CircuitBreakerStrategy(failure_threshold=5, recovery_timeout=60.0)
    
    handler.register_recovery_strategy(retry_strategy)
    handler.register_recovery_strategy(circuit_breaker)
    
    # Añadir configuraciones de error
    handler.add_error_config(ErrorActionConfig(
        action=ErrorAction.RETRY,
        condition=lambda ctx: ctx.severity in [ErrorSeverity.MEDIUM, ErrorSeverity.LOW]
    ))
    
    handler.add_error_config(ErrorActionConfig(
        action=ErrorAction.ESCALATE,
        condition=lambda ctx: ctx.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]
    ))
    
    handler.add_error_config(ErrorActionConfig(
        action=ErrorAction.CIRCUIT_BREAKER,
        condition=lambda ctx: ctx.error_type == ErrorType.NETWORK_ERROR
    ))
    
    return handler


def create_default_priority_manager() -> PriorityManager:
    """Crear gestor de priorización con reglas por defecto."""
    
    manager = PriorityManager()
    manager.add_default_rules()
    return manager