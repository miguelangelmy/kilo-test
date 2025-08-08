# Sistema de Línea de Ensamblaje Multiagente

Sistema distribuido de línea de ensamblaje que utiliza agentes inteligentes coordinados mediante comunicación XMPP.

## Descripción

Este proyecto implementa un sistema de línea de ensamblaje multiagente que permite la coordinación entre diferentes tipos de agentes (cinta transportadora, grúas, brazos robóticos, estaciones de ensamblaje) utilizando la comunicación XMPP con un servidor ejabberd.

## Estructura del Proyecto

```
assembly_line_system/
├── agents/              # Implementaciones de agentes
│   ├── __init__.py      # Módulo de inicialización
│   ├── base_agent.py    # Clase base para agentes
│   ├── conveyor_agent.py # Agente de cinta transportadora
│   ├── crane_agent.py   # Agente de grúa
│   ├── robotic_arm_agent.py # Agente de brazo robótico
│   └── assembly_station_agent.py # Agente de estación de ensamblaje
├── protocols/           # Protocolos de comunicación
│   └── material_transfer.py # Protocolo de transferencia de materiales
├── config.py            # Configuración del sistema
└── utils/               # Utilidades auxiliares

examples/
├── xmpp_demo.py         # Demostración de uso
```

## Agentes Implementados

### 1. Agente de Cinta Transportadora (`ConveyorAgent`)
- Coordina el movimiento de materiales a través de la línea
- Gestiona la capacidad de aceptar transferencias

### 2. Agente de Grúa (`CraneAgent`)
- Realiza operaciones de levantamiento y transporte pesado
- Gestiona transferencias de materiales grandes

### 3. Agente de Brazo Robótico (`RoboticArmAgent`)
- Realiza operaciones precisas de manipulación
- Coordinación con estaciones de ensamblaje

### 4. Agente de Estación de Ensamblaje (`AssemblyStationAgent`)
- Realiza operaciones finales de ensamblaje
- Gestiona la aceptación y procesamiento de materiales

## Comunicación XMPP

El sistema utiliza el protocolo XMPP para la comunicación entre agentes. La configuración está definida en `config.py`:

```python
XMPP_CONFIG = {
    'server': 'localhost',
    'port': 5222,
    'domain': 'ejabberd.local',
    'admin_user': 'admin',
    'admin_password': 'secreta'
}
```

## Características Principales

- **Arquitectura modular**: Facilita la extensión con nuevos tipos de agentes
- **Protocolo de transferencia robusto**: Manejo completo de solicitudes, respuestas y rechazos
- **Capacidades XMPP**: Métodos base para comunicación entre agentes
- **Configuración centralizada**: Todos los parámetros del sistema en un solo lugar

## Uso

Para ejecutar la demostración:

```bash
python examples/xmpp_demo.py
```

## Requisitos

- Python 3.7+
- Paquetes requeridos (ver `requirements.txt`)

## Configuración del Servidor XMPP

El sistema está configurado para trabajar con un servidor ejabberd en `localhost:5222` usando las credenciales:
- Usuario administrador: admin
- Contraseña: secreta

## Desarrollo

Para agregar nuevos agentes, extender el sistema o modificar la comunicación XMPP:

1. Crear una nueva clase de agente que herede de `AssemblyLineAgent`
2. Implementar los métodos necesarios para la comunicación XMPP
3. Añadir el agente al módulo `__init__.py` en la carpeta de agents
4. Actualizar el archivo de configuración si es necesario

## Licencia

[MIT License](LICENSE)