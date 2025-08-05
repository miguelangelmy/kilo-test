"""
Sistema de persistencia e historial completo para el sistema multiagente.

Este módulo proporciona funcionalidades para:
- Persistir el estado completo del ProtocolManager
- Guardar historial de mensajes y errores
- Recuperar estado después de reinicios
- Backup automático y restauración
"""

import json
import pickle
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MessageRecord:
    """Registro de mensaje persistente."""
    message_id: str
    timestamp: datetime
    sender: str
    receiver: str
    protocol_type: str
    content: Dict[str, Any]
    priority: int
    status: str  # 'sent', 'delivered', 'failed', 'processed'
    session_id: Optional[str] = None
    error_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageRecord':
        """Crear desde diccionario."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ErrorRecord:
    """Registro de error persistente."""
    error_id: str
    timestamp: datetime
    agent_id: str
    error_type: str
    severity: int
    message: str
    context: Dict[str, Any]
    action_taken: str
    recovery_attempts: int
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorRecord':
        """Crear desde diccionario."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class SessionRecord:
    """Registro de sesión persistente."""
    session_id: str
    timestamp: datetime
    agent_id: str
    protocol_type: str
    status: str  # 'active', 'completed', 'failed', 'timeout'
    start_time: datetime
    end_time: Optional[datetime] = None
    messages_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionRecord':
        """Crear desde diccionario."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


class PersistenceManager:
    """Gestor de persistencia para el sistema multiagente."""
    
    def __init__(self, db_path: str = "assembly_line_state.db", 
                 backup_dir: str = "backups",
                 auto_backup_interval: int = 300):  # 5 minutos
        """
        Inicializar el gestor de persistencia.
        
        Args:
            db_path: Ruta a la base de datos SQLite
            backup_dir: Directorio para backups automáticos
            auto_backup_interval: Intervalo de backup en segundos
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.auto_backup_interval = auto_backup_interval
        
        # Crear directorios si no existen
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
        
        # Configurar backup automático
        self.backup_timer = None
        self._start_auto_backup()
        
        # Lock para concurrencia
        self.lock = threading.Lock()
        
        logger.info(f"PersistenceManager inicializado en {self.db_path}")
    
    def _init_database(self):
        """Inicializar las tablas de la base de datos."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Tabla de mensajes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    protocol_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    session_id TEXT,
                    error_info TEXT
                )
            ''')
            
            # Tabla de errores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    error_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    context TEXT NOT NULL,
                    action_taken TEXT NOT NULL,
                    recovery_attempts INTEGER NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabla de sesiones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    protocol_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    messages_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de estadísticas diarias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    messages_sent INTEGER DEFAULT 0,
                    messages_delivered INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    sessions_completed INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
    
    def _start_auto_backup(self):
        """Iniciar el backup automático."""
        if self.backup_timer:
            self.backup_timer.cancel()
        
        def auto_backup():
            try:
                self.create_backup()
                logger.info("Backup automático completado")
            except Exception as e:
                logger.error(f"Error en backup automático: {e}")
            
            # Programar próximo backup
            self.backup_timer = threading.Timer(self.auto_backup_interval, auto_backup)
            self.backup_timer.start()
        
        # Iniciar primer backup
        self.backup_timer = threading.Timer(self.auto_backup_interval, auto_backup)
        self.backup_timer.start()
    
    def save_message_record(self, message: MessageRecord):
        """Guardar un registro de mensaje."""
        with self.lock:
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO messages 
                        (message_id, timestamp, sender, receiver, protocol_type, content, priority, status, session_id, error_info)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        message.message_id,
                        message.timestamp.isoformat(),
                        message.sender,
                        message.receiver,
                        message.protocol_type,
                        json.dumps(message.content),
                        message.priority,
                        message.status,
                        message.session_id,
                        json.dumps(message.error_info) if message.error_info else None
                    ))
                    conn.commit()
                logger.debug(f"Mensaje guardado: {message.message_id}")
            except Exception as e:
                logger.error(f"Error al guardar mensaje: {e}")
    
    def save_error_record(self, error: ErrorRecord):
        """Guardar un registro de error."""
        with self.lock:
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO errors 
                        (error_id, timestamp, agent_id, error_type, severity, message, context, action_taken, recovery_attempts, resolved)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        error.error_id,
                        error.timestamp.isoformat(),
                        error.agent_id,
                        error.error_type,
                        error.severity,
                        error.message,
                        json.dumps(error.context),
                        error.action_taken,
                        error.recovery_attempts,
                        error.resolved
                    ))
                    conn.commit()
                logger.debug(f"Error guardado: {error.error_id}")
            except Exception as e:
                logger.error(f"Error al guardar error: {e}")
    
    def save_session_record(self, session: SessionRecord):
        """Guardar un registro de sesión."""
        with self.lock:
            try:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO sessions 
                        (session_id, timestamp, agent_id, protocol_type, status, start_time, end_time, messages_count, error_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session.session_id,
                        session.timestamp.isoformat(),
                        session.agent_id,
                        session.protocol_type,
                        session.status,
                        session.start_time.isoformat(),
                        session.end_time.isoformat() if session.end_time else None,
                        session.messages_count,
                        session.error_count
                    ))
                    conn.commit()
                logger.debug(f"Sesión guardada: {session.session_id}")
            except Exception as e:
                logger.error(f"Error al guardar sesión: {e}")
    
    def get_message_history(self, agent_id: Optional[str] = None, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           limit: int = 1000) -> List[MessageRecord]:
        """Obtener historial de mensajes."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM messages WHERE 1=1"
                params = []
                
                if agent_id:
                    query += " AND (sender = ? OR receiver = ?)"
                    params.extend([agent_id, agent_id])
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                messages = []
                for row in rows:
                    message_data = {
                        'message_id': row[0],
                        'timestamp': datetime.fromisoformat(row[1]),
                        'sender': row[2],
                        'receiver': row[3],
                        'protocol_type': row[4],
                        'content': json.loads(row[5]),
                        'priority': row[6],
                        'status': row[7],
                        'session_id': row[8],
                        'error_info': json.loads(row[9]) if row[9] else None
                    }
                    messages.append(MessageRecord.from_dict(message_data))
                
                return messages
        except Exception as e:
            logger.error(f"Error al obtener historial de mensajes: {e}")
            return []
    
    def get_error_history(self, agent_id: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 1000) -> List[ErrorRecord]:
        """Obtener historial de errores."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM errors WHERE 1=1"
                params = []
                
                if agent_id:
                    query += " AND agent_id = ?"
                    params.append(agent_id)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                errors = []
                for row in rows:
                    error_data = {
                        'error_id': row[0],
                        'timestamp': datetime.fromisoformat(row[1]),
                        'agent_id': row[2],
                        'error_type': row[3],
                        'severity': row[4],
                        'message': row[5],
                        'context': json.loads(row[6]),
                        'action_taken': row[7],
                        'recovery_attempts': row[8],
                        'resolved': bool(row[9])
                    }
                    errors.append(ErrorRecord.from_dict(error_data))
                
                return errors
        except Exception as e:
            logger.error(f"Error al obtener historial de errores: {e}")
            return []
    
    def get_session_history(self, agent_id: Optional[str] = None,
                           protocol_type: Optional[str] = None,
                           limit: int = 1000) -> List[SessionRecord]:
        """Obtener historial de sesiones."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM sessions WHERE 1=1"
                params = []
                
                if agent_id:
                    query += " AND agent_id = ?"
                    params.append(agent_id)
                
                if protocol_type:
                    query += " AND protocol_type = ?"
                    params.append(protocol_type)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    session_data = {
                        'session_id': row[0],
                        'timestamp': datetime.fromisoformat(row[1]),
                        'agent_id': row[2],
                        'protocol_type': row[3],
                        'status': row[4],
                        'start_time': datetime.fromisoformat(row[5]),
                        'end_time': datetime.fromisoformat(row[6]) if row[6] else None,
                        'messages_count': row[7],
                        'error_count': row[8]
                    }
                    sessions.append(SessionRecord.from_dict(session_data))
                
                return sessions
        except Exception as e:
            logger.error(f"Error al obtener historial de sesiones: {e}")
            return []
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Obtener estadísticas del sistema."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Estadísticas generales
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_messages,
                        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_messages,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_messages,
                        COUNT(DISTINCT session_id) as total_sessions
                    FROM messages 
                    WHERE timestamp >= ? AND timestamp <= ?
                ''', (start_date.isoformat(), end_date.isoformat()))
                
                msg_stats = cursor.fetchone()
                
                # Estadísticas de errores
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_errors,
                        SUM(CASE WHEN resolved = 1 THEN 1 ELSE 0 END) as resolved_errors,
                        AVG(severity) as avg_severity
                    FROM errors 
                    WHERE timestamp >= ? AND timestamp <= ?
                ''', (start_date.isoformat(), end_date.isoformat()))
                
                error_stats = cursor.fetchone()
                
                # Estadísticas de sesiones
                cursor.execute('''
                    SELECT 
                        COUNT(*) as completed_sessions,
                        AVG(messages_count) as avg_messages_per_session,
                        AVG(error_count) as avg_errors_per_session
                    FROM sessions 
                    WHERE status = 'completed' AND timestamp >= ? AND timestamp <= ?
                ''', (start_date.isoformat(), end_date.isoformat()))
                
                session_stats = cursor.fetchone()
                
                return {
                    'period_days': days,
                    'message_statistics': {
                        'total_messages': msg_stats[0] if msg_stats[0] else 0,
                        'delivered_messages': msg_stats[1] if msg_stats[1] else 0,
                        'failed_messages': msg_stats[2] if msg_stats[2] else 0,
                        'success_rate': (msg_stats[1] / msg_stats[0] * 100) if msg_stats[0] and msg_stats[1] else 0
                    },
                    'error_statistics': {
                        'total_errors': error_stats[0] if error_stats[0] else 0,
                        'resolved_errors': error_stats[1] if error_stats[1] else 0,
                        'resolution_rate': (error_stats[1] / error_stats[0] * 100) if error_stats[0] and error_stats[1] else 0,
                        'average_severity': error_stats[2] if error_stats[2] else 0
                    },
                    'session_statistics': {
                        'completed_sessions': session_stats[0] if session_stats[0] else 0,
                        'average_messages_per_session': session_stats[1] if session_stats[1] else 0,
                        'average_errors_per_session': session_stats[2] if session_stats[2] else 0
                    }
                }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def create_backup(self) -> str:
        """Crear un backup completo del estado."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.db"
        
        try:
            # Copiar la base de datos actual
            import shutil
            shutil.copy2(str(self.db_path), str(backup_file))
            
            # Crear backup de estado en JSON
            state_backup = {
                'timestamp': timestamp,
                'database_path': str(backup_file),
                'statistics': self.get_statistics()
            }
            
            state_file = self.backup_dir / f"state_{timestamp}.json"
            with open(state_file, 'w') as f:
                json.dump(state_backup, f, indent=2)
            
            logger.info(f"Backup creado: {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Error al crear backup: {e}")
            return ""
    
    def restore_from_backup(self, backup_file: str) -> bool:
        """Restaurar desde un backup."""
        try:
            import shutil
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                logger.error(f"Backup no encontrado: {backup_file}")
                return False
            
            # Detener backup automático
            if self.backup_timer:
                self.backup_timer.cancel()
            
            # Restaurar base de datos
            shutil.copy2(str(backup_path), str(self.db_path))
            
            # Reiniciar backup automático
            self._start_auto_backup()
            
            logger.info(f"Restauración completada desde: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error al restaurar backup: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Limpiar datos antiguos."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Eliminar mensajes antiguos
                cursor.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff_date.isoformat(),))
                
                # Eliminar errores resueltos antiguos
                cursor.execute("DELETE FROM errors WHERE resolved = 1 AND timestamp < ?", (cutoff_date.isoformat(),))
                
                # Eliminar sesiones completadas antiguas
                cursor.execute("DELETE FROM sessions WHERE status = 'completed' AND timestamp < ?", (cutoff_date.isoformat(),))
                
                conn.commit()
            
            logger.info(f"Datos antiguos limpiados (más de {days_to_keep} días)")
        except Exception as e:
            logger.error(f"Error al limpiar datos antiguos: {e}")
    
    def export_data(self, output_file: str, format_type: str = 'json', 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None):
        """Exportar datos a archivo."""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                },
                'messages': [msg.to_dict() for msg in self.get_message_history(
                    start_date=start_date, end_date=end_date, limit=10000
                )],
                'errors': [error.to_dict() for error in self.get_error_history(
                    start_date=start_date, end_date=end_date, limit=10000
                )],
                'sessions': [session.to_dict() for session in self.get_session_history(limit=1000)],
                'statistics': self.get_statistics()
            }
            
            output_path = Path(output_file)
            
            if format_type.lower() == 'json':
                with open(output_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
            elif format_type.lower() == 'csv':
                # Exportar a CSV (simplificado)
                import csv
                
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Exportar mensajes
                    writer.writerow(['Message_ID', 'Timestamp', 'Sender', 'Receiver', 'Status'])
                    for msg in export_data['messages']:
                        writer.writerow([
                            msg['message_id'], msg['timestamp'], 
                            msg['sender'], msg['receiver'], msg['status']
                        ])
            
            logger.info(f"Datos exportados a: {output_file}")
        except Exception as e:
            logger.error(f"Error al exportar datos: {e}")


# Funciones de utilidad
def create_default_persistence_manager() -> PersistenceManager:
    """Crear gestor de persistencia con configuración por defecto."""
    return PersistenceManager()


def create_test_persistence_manager() -> PersistenceManager:
    """Crear gestor de persistencia para pruebas."""
    import tempfile
    import os
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_assembly_line.db")
    
    return PersistenceManager(db_path=db_path, backup_dir=temp_dir)