"""
ProtocolManager con procesamiento asíncrono.

Este módulo implementa un gestor de protocolos avanzado que maneja
comunicación asíncrona entre agentes, con priorización y manejo de errores.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from queue import PriorityQueue
import threading
import time

from spade.message import Message
from spade.behaviour import CyclicBehaviour
from spade.agent import Agent

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Prioridades para mensajes de comunicación."""
    CRITICAL = 1      # Mensajes críticos que requieren atención inmediata
    HIGH = 2          # Mensajes de alta prioridad
    NORMAL = 3        # Mensajes normales
    LOW = 4           # Mensajes de baja prioridad
    BACKGROUND = 5     # Tareas en segundo plano


class ProtocolState(Enum):
    """Estados del protocolo de comunicación."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_RESPONSE = "waiting_response"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class MessageTask:
    """Tarea de mensaje con priorización."""
    
    priority: MessagePriority
    timestamp: datetime = field(default_factory=datetime.now)
    message: Message = None
    callback: Callable = None
    timeout: float = 30.0  # segundos
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Comparación para PriorityQueue - prioridad más alta primero."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.timestamp < other.timestamp


@dataclass
class ProtocolSession:
    """Sesión de protocolo activa."""
    
    session_id: str
    protocol_type: str
    source_agent: str
    target_agent: str
    state: ProtocolState = ProtocolState.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    timeout: float = 60.0
    messages_sent: int = 0
    messages_received: int = 0
    error_count: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Verificar si la sesión ha expirado."""
        return (datetime.now() - self.last_activity).total_seconds() > self.timeout
    
    def update_activity(self):
        """Actualizar la última actividad de la sesión."""
        self.last_activity = datetime.now()


class ProtocolManager(CyclicBehaviour):
    """
    Gestor de protocolos con procesamiento asíncrono.
    
    Este comportamiento gestiona todas las comunicaciones entre agentes
    con priorización, manejo de errores y persistencia de sesiones.
    """
    
    def __init__(self, agent: Agent):
        super().__init__()
        self.agent = agent
        self.message_queue = PriorityQueue()
        self.active_sessions: Dict[str, ProtocolSession] = {}
        self.protocol_handlers: Dict[str, Callable] = {}
        self.session_timeout_callbacks: Dict[str, Callable] = {}
        
        # Configuración
        self.max_queue_size = 1000
        self.session_cleanup_interval = 300.0  # 5 minutos
        self.last_cleanup = datetime.now()
        
        # Hilos para procesamiento asíncrono
        self.processing_thread = None
        self.running = False
        
        # Estadísticas
        self.stats = {
            'messages_processed': 0,
            'sessions_created': 0,
            'sessions_completed': 0,
            'sessions_expired': 0,
            'errors_encountered': 0
        }
        
    def setup(self):
        """Configurar el gestor de protocolos."""
        logger.info(f"Setup ProtocolManager for agent {self.agent.agent_id}")
        
        # Registrar manejadores de protocolos
        self.register_protocol_handler("material_transfer", self._handle_material_transfer)
        
        # Iniciar procesamiento asíncrono
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_messages_async)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def register_protocol_handler(self, protocol_name: str, handler: Callable):
        """Registrar un manejador para un tipo de protocolo."""
        self.protocol_handlers[protocol_name] = handler
        logger.info(f"Registered handler for protocol: {protocol_name}")
    
    def register_session_timeout_callback(self, session_id: str, callback: Callable):
        """Registrar callback para timeout de sesión."""
        self.session_timeout_callbacks[session_id] = callback
    
    def send_message_with_priority(self, 
                                 message: Message, 
                                 priority: MessagePriority = MessagePriority.NORMAL,
                                 callback: Callable = None,
                                 timeout: float = 30.0,
                                 metadata: Dict[str, Any] = None) -> str:
        """
        Enviar mensaje con priorización específica.
        
        Args:
            message: Mensaje a enviar
            priority: Prioridad del mensaje
            callback: Función de callback al completar
            timeout: Tiempo máximo de espera
            metadata: Datos adicionales
            
        Returns:
            ID de la tarea creada
        """
        
        # Verificar límite de cola
        if self.message_queue.qsize() >= self.max_queue_size:
            logger.warning("Message queue full, dropping message")
            return None
        
        # Crear tarea de mensaje
        task = MessageTask(
            priority=priority,
            message=message,
            callback=callback,
            timeout=timeout,
            metadata=metadata or {}
        )
        
        # Agregar a cola
        self.message_queue.put(task)
        logger.info(f"Message queued with priority {priority.name} for {message.to}")
        
        return f"task_{id(task)}"
    
    def create_protocol_session(self, 
                              session_id: str,
                              protocol_type: str,
                              source_agent: str,
                              target_agent: str,
                              timeout: float = 60.0) -> ProtocolSession:
        """
        Crear una nueva sesión de protocolo.
        
        Args:
            session_id: ID único de la sesión
            protocol_type: Tipo de protocolo
            source_agent: Agente origen
            target_agent: Agente destino
            timeout: Tiempo de espera en segundos
            
        Returns:
            Sesión creada
        """
        
        session = ProtocolSession(
            session_id=session_id,
            protocol_type=protocol_type,
            source_agent=source_agent,
            target_agent=target_agent,
            timeout=timeout
        )
        
        self.active_sessions[session_id] = session
        self.stats['sessions_created'] += 1
        
        logger.info(f"Created protocol session {session_id} for {protocol_type}")
        return session
    
    def update_session_state(self, 
                           session_id: str, 
                           state: ProtocolState,
                           data: Dict[str, Any] = None):
        """Actualizar estado de una sesión activa."""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.state = state
            session.update_activity()
            
            if data:
                session.data.update(data)
            
            logger.debug(f"Session {session_id} state updated to {state.value}")
    
    def get_session(self, session_id: str) -> Optional[ProtocolSession]:
        """Obtener sesión activa por ID."""
        return self.active_sessions.get(session_id)
    
    def cleanup_expired_sessions(self):
        """Limpiar sesiones expiradas."""
        
        expired_sessions = []
        for session_id, session in self.active_sessions.items():
            if session.is_expired():
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.active_sessions[session_id]
            
            # Ejecutar callback de timeout si existe
            if session_id in self.session_timeout_callbacks:
                try:
                    self.session_timeout_callbacks[session_id](session)
                except Exception as e:
                    logger.error(f"Error in timeout callback for session {session_id}: {e}")
            
            # Registrar estadísticas
            self.stats['sessions_expired'] += 1
            
            logger.warning(f"Session {session_id} expired after {timeout}s")
            del self.active_sessions[session_id]
    
    def _process_messages_async(self):
        """Procesamiento asíncrono de mensajes en hilo separado."""
        
        while self.running:
            try:
                # Obtener siguiente mensaje de la cola
                task = self.message_queue.get(timeout=1.0)
                
                # Procesar mensaje
                self._process_message_task(task)
                
            except Exception as e:
                if not isinstance(e, queue.Empty):
                    logger.error(f"Error in async message processing: {e}")
                
                time.sleep(0.1)
    
    def _process_message_task(self, task: MessageTask):
        """Procesar una tarea de mensaje."""
        
        try:
            # Enviar mensaje
            self.send(task.message)
            
            # Actualizar estadísticas
            self.stats['messages_processed'] += 1
            
            logger.info(f"Message sent to {task.message.to} with priority {task.priority.name}")
            
            # Ejecutar callback si existe
            if task.callback:
                try:
                    task.callback(task.message, "success")
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")
                    
        except Exception as e:
            self.stats['errors_encountered'] += 1
            logger.error(f"Failed to send message: {e}")
            
            # Reintentar si es posible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"Retrying message (attempt {task.retry_count}/{task.max_retries})")
                
                # Reagregar a cola con mayor prioridad
                task.priority = MessagePriority.HIGH  # Incrementar prioridad en retry
                self.message_queue.put(task)
            else:
                # Notificar error a callback
                if task.callback:
                    try:
                        task.callback(task.message, "failed")
                    except Exception as e:
                        logger.error(f"Error in error callback: {e}")
    
    def _handle_material_transfer(self, msg: Message) -> Optional[Message]:
        """Manejar protocolo de transferencia de materiales."""
        
        try:
            content = json.loads(msg.body)
            
            # Verificar tipo de mensaje
            message_type = content.get("message_type")
            
            if message_type == "material_transfer_request":
                return self._handle_material_request(msg, content)
            elif message_type == "material_transfer_execute":
                return self._handle_material_execute(msg, content)
            else:
                logger.warning(f"Unknown material transfer message type: {message_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error handling material transfer: {e}")
            return None
    
    def _handle_material_request(self, msg: Message, content: Dict) -> Optional[Message]:
        """Manejar solicitud de transferencia de materiales."""
        
        # Crear sesión si no existe
        session_id = f"transfer_{content.get('source')}_{self.agent.agent_id}_{int(time.time())}"
        
        session = self.create_protocol_session(
            session_id=session_id,
            protocol_type="material_transfer",
            source_agent=content.get('source'),
            target_agent=self.agent.agent_id
        )
        
        # Actualizar estado de sesión
        self.update_session_state(session_id, ProtocolState.WAITING_RESPONSE)
        
        # Aquí iría la lógica específica del agente
        # Por ahora, simulamos una respuesta positiva
        response_content = {
            "message_type": "material_transfer_confirm",
            "session_id": session_id,
            "ready_time": int(time.time()) + 5,  # Listo en 5 segundos
            "status": "ready"
        }
        
        response = Message(to=msg.sender, body=json.dumps(response_content))
        
        # Actualizar estadísticas de sesión
        session.messages_received += 1
        
        return response
    
    def _handle_material_execute(self, msg: Message, content: Dict) -> Optional[Message]:
        """Manejar ejecución de transferencia de materiales."""
        
        session_id = content.get('session_id')
        if not session_id:
            logger.error("Missing session_id in execute message")
            return None
        
        # Actualizar estado de sesión
        self.update_session_state(session_id, ProtocolState.PROCESSING)
        
        # Aquí iría la lógica específica del agente
        # Por ahora, simulamos una ejecución exitosa
        
        response_content = {
            "message_type": "material_transfer_complete",
            "session_id": session_id,
            "status": "success",
            "timestamp": int(time.time())
        }
        
        response = Message(to=msg.sender, body=json.dumps(response_content))
        
        # Actualizar estadísticas de sesión
        session = self.get_session(session_id)
        if session:
            session.messages_sent += 1
            self.update_session_state(session_id, ProtocolState.COMPLETED)
        
        return response
    
    def _on_message(self, msg: Message):
        """Manejar mensajes entrantes."""
        
        try:
            # Parsear contenido
            content = json.loads(msg.body)
            
            # Obtener tipo de protocolo
            protocol_type = content.get("message_type", "").split("_")[0]  # material_transfer -> material
            
            # Buscar manejador de protocolo
            handler = self.protocol_handlers.get(protocol_type)
            
            if handler:
                response = handler(msg)
                
                # Enviar respuesta si existe
                if response:
                    self.send(response)
            else:
                logger.warning(f"No handler found for protocol: {protocol_type}")
                
        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
    
    def run(self):
        """Bucle principal del comportamiento."""
        
        while self.running:
            try:
                # Limpiar sesiones expiradas periódicamente
                if (datetime.now() - self.last_cleanup).total_seconds() > self.session_cleanup_interval:
                    self.cleanup_expired_sessions()
                    self.last_cleanup = datetime.now()
                
                # Procesar mensajes entrantes
                msg = self.receive(timeout=1.0)
                if msg:
                    self._on_message(msg)
                
            except Exception as e:
                logger.error(f"Error in ProtocolManager main loop: {e}")
    
    def stop(self):
        """Detener el gestor de protocolos."""
        
        self.running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        
        logger.info(f"ProtocolManager stopped for agent {self.agent.agent_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del gestor de protocolos."""
        
        active_sessions_count = len(self.active_sessions)
        
        # Calcular distribución de estados
        session_states = {}
        for session in self.active_sessions.values():
            state_key = session.state.value
            session_states[state_key] = session_states.get(state_key, 0) + 1
        
        return {
            **self.stats,
            'active_sessions': active_sessions_count,
            'queue_size': self.message_queue.qsize(),
            'session_states': session_states
        }