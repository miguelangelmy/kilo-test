"""
Robotic Arm Agent implementation for the assembly line system.
"""

from assembly_line_system.agents.base_agent import AssemblyLineAgent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import json
import random

class RoboticArmAgent(AssemblyLineAgent):
    """
    Agent representing a robotic arm in the assembly line.

    Responsibilities:
    - Precise manipulation of materials and components
    - Assembly operations with high accuracy
    - Quality control and inspection tasks
    - Flexible task switching based on production needs
    """

    def __init__(self, agent_id, jid, password, env):
        """
        Initialize the robotic arm agent.

        Args:
            agent_id (str): Unique identifier for the agent
            jid (str): JID for XMPP communication
            password (str): Password for XMPP authentication
            env: Reference to the shared environment
        """
        super().__init__(agent_id, jid, password, env)

        # Robotic arm-specific attributes
        self.arm_reach = 50.0  # Maximum reach (units)
        self.precision_level = 0.98  # Precision level (0-1)
        self.current_task = None
        self.task_queue = []
        self.gripper_status = "open"  # open, closed, error
        self.end_effector_type = "universal"  # universal, specialized, custom
        self.maintenance_cycles = 0
        self.max_maintenance_cycles = 100
        
    def _setup_cyclic_behaviour(self):
        """Set up cyclic behavior for continuous operation."""
        class RoboticArmCyclicBehaviour(CyclicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Robotic arm cyclic behaviour running")

                # Check maintenance status
                if self._needs_maintenance():
                    await self._perform_maintenance()
                else:
                    # Process current task or get new one
                    if self.current_task is None and self.task_queue:
                        await self._start_next_task()
                    
                    if self.current_task:
                        await self._execute_current_task()
                    else:
                        await self._scan_for_tasks()

        return RoboticArmCyclicBehaviour()

    def _setup_periodic_behaviour(self):
        """Set up periodic behavior for regular tasks."""
        class RoboticArmPeriodicBehaviour(PeriodicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Robotic arm periodic behaviour running")

                # Optimize task queue
                await self._optimize_task_queue()
                
                # Check calibration
                await self._check_calibration()
                
                # Update skills based on experience
                await self._update_skills()

        return RoboticArmPeriodicBehaviour(period=8)  # Check every 8 time steps

    async def _scan_for_tasks(self):
        """Scan for available tasks in the environment."""
        print(f"{self.agent_id}: Scanning for available tasks")
        
        # Simulate scanning environment for tasks
        available_tasks = self._get_available_tasks()
        
        for task in available_tasks:
            if self._can_perform_task(task):
                self.task_queue.append(task)
                print(f"{self.agent_id}: Added task {task['id']} to queue")
                
        # Sort tasks by priority
        self.task_queue.sort(key=lambda t: t.get('priority', 1), reverse=True)

    async def _start_next_task(self):
        """Start the next task from the queue."""
        if self.task_queue:
            self.current_task = self.task_queue.pop(0)
            print(f"{self.agent_id}: Started task {self.current_task['id']}")
            
            # Prepare for the task
            await self._prepare_for_task(self.current_task)

    async def _execute_current_task(self):
        """Execute the current task."""
        if not self.current_task:
            return
            
        print(f"{self.agent_id}: Executing task {self.current_task['id']}")
        
        task_type = self.current_task.get('type', 'assembly')
        
        if task_type == 'assembly':
            await self._perform_assembly_task()
        elif task_type == 'inspection':
            await self._perform_inspection_task()
        elif task_type == 'quality_control':
            await self._perform_quality_control_task()
        elif task_type == 'material_handling':
            await self._perform_material_handling_task()
            
        # Check if task is complete
        if random.random() < 0.9:  # 90% chance of task completion per cycle
            await self._complete_current_task()
        else:
            print(f"{self.agent_id}: Task {self.current_task['id']} in progress")

    async def _perform_assembly_task(self):
        """Perform an assembly task."""
        print(f"{self.agent_id}: Performing assembly task")
        
        # Simulate precise assembly operations
        success_probability = self.precision_level * (1 - self.maintenance_cycles / self.max_maintenance_cycles)
        
        if random.random() < success_probability:
            # Successful assembly
            self.current_task['progress'] = min(1.0, self.current_task.get('progress', 0) + 0.2)
            print(f"{self.agent_id}: Assembly progress: {self.current_task['progress']:.2f}")
        else:
            # Assembly failed due to precision issues
            print(f"{self.agent_id}: Assembly precision issue")
            
        # Update maintenance cycles
        self.maintenance_cycles += 1

    async def _perform_inspection_task(self):
        """Perform an inspection task."""
        print(f"{self.agent_id}: Performing inspection task")
        
        # Simulate inspection with high precision
        detection_rate = self.precision_level * 0.95
        
        if random.random() < detection_rate:
            # Successfully detected issue
            self.current_task['progress'] = min(1.0, self.current_task.get('progress', 0) + 0.3)
            print(f"{self.agent_id}: Inspection progress: {self.current_task['progress']:.2f}")
        else:
            # Missed issue
            print(f"{self.agent_id}: Inspection missed potential issue")

    async def _perform_quality_control_task(self):
        """Perform a quality control task."""
        print(f"{self.agent_id}: Performing quality control")
        
        # Simulate quality assessment
        accuracy = self.precision_level * 0.9
        
        if random.random() < accuracy:
            # Accurate quality assessment
            self.current_task['progress'] = min(1.0, self.current_task.get('progress', 0) + 0.25)
            print(f"{self.agent_id}: Quality control progress: {self.current_task['progress']:.2f}")
        else:
            # Inaccurate assessment
            print(f"{self.agent_id}: Quality control inaccuracy")

    async def _perform_material_handling_task(self):
        """Perform material handling task."""
        print(f"{self.agent_id}: Performing material handling")
        
        # Simulate precise material manipulation
        success_rate = self.precision_level * 0.85
        
        if random.random() < success_rate:
            # Successful material handling
            self.current_task['progress'] = min(1.0, self.current_task.get('progress', 0) + 0.15)
            print(f"{self.agent_id}: Material handling progress: {self.current_task['progress']:.2f}")
        else:
            # Handling failed
            print(f"{self.agent_id}: Material handling error")

    async def _complete_current_task(self):
        """Complete the current task."""
        if self.current_task:
            print(f"{self.agent_id}: Completed task {self.current_task['id']}")
            
            # Calculate task reward
            quality = self.current_task.get('quality', 0.8)
            efficiency = 1.0 - (self.current_task.get('duration', 10) / 20)
            
            task_reward = quality * efficiency
            print(f"{self.agent_id}: Task reward: {task_reward:.2f}")
            
            self.current_task = None
            self.gripper_status = "open"  # Reset gripper

    async def _prepare_for_task(self, task):
        """Prepare the robotic arm for a specific task."""
        print(f"{self.agent_id}: Preparing for task {task['id']}")
        
        # Configure end effector based on task type
        task_type = task.get('type', 'assembly')
        
        if task_type == 'assembly':
            self.end_effector_type = "specialized_assembly"
        elif task_type == 'inspection':
            self.end_effector_type = "high_precision_camera"
        elif task_type == 'quality_control':
            self.end_effector_type = "multi_sensor"
        else:
            self.end_effector_type = "universal"
            
        # Close gripper if needed
        if task.get('requires_gripper', False):
            self.gripper_status = "closed"
            
        print(f"{self.agent_id}: Configured with {self.end_effector_type} end effector")

    async def _optimize_task_queue(self):
        """Optimize the task queue for efficiency."""
        print(f"{self.agent_id}: Optimizing task queue")
        
        # Reorder tasks based on current conditions
        self.task_queue.sort(key=lambda t: (
            t.get('priority', 1),
            -t.get('urgency', 0.5),  # Higher urgency first
            t.get('duration', 10)    # Shorter tasks first
        ))
        
        print(f"{self.agent_id}: Queue optimized, {len(self.task_queue)} tasks remaining")

    async def _check_calibration(self):
        """Check and maintain calibration."""
        print(f"{self.agent_id}: Checking calibration")
        
        # Random chance of calibration drift
        if random.random() < 0.1:  # 10% chance per check
            self.precision_level = max(0.7, self.precision_level - 0.05)
            print(f"{self.agent_id}: Calibration degraded, precision: {self.precision_level:.3f}")
        else:
            # Gradual improvement through self-correction
            self.precision_level = min(1.0, self.precision_level + 0.01)
            print(f"{self.agent_id}: Calibration maintained, precision: {self.precision_level:.3f}")

    async def _update_skills(self):
        """Update skills based on experience."""
        print(f"{self.agent_id}: Updating skills")
        
        # Skill improvement through learning
        if self.current_task:
            task_type = self.current_task.get('type', 'assembly')
            
            if task_type == 'assembly':
                self.precision_level = min(1.0, self.precision_level + 0.001)
            elif task_type == 'inspection':
                # Inspection skills improve detection rate
                pass  # Already handled in precision

    def _needs_maintenance(self):
        """Check if robotic arm needs maintenance."""
        return (self.maintenance_cycles >= self.max_maintenance_cycles or 
                random.random() < 0.05)  # 5% chance of unexpected maintenance

    async def _perform_maintenance(self):
        """Perform maintenance on the robotic arm."""
        print(f"{self.agent_id}: Performing maintenance")
        
        # Reset maintenance cycles
        self.maintenance_cycles = 0
        
        # Improve precision after maintenance
        self.precision_level = min(1.0, self.precision_level + 0.05)
        
        # Reset gripper status
        self.gripper_status = "open"
        
        print(f"{self.agent_id}: Maintenance complete, precision: {self.precision_level:.3f}")

    def _can_perform_task(self, task):
        """Check if robotic arm can perform a specific task."""
        # Check task compatibility with end effector
        required_effector = task.get('required_effector', 'universal')
        
        if (required_effector == 'specialized_assembly' and 
            self.end_effector_type != 'specialized_assembly'):
            return False
            
        # Check if arm has capacity
        if len(self.task_queue) >= 5:  # Max queue size
            return False
            
        return True

    def _get_available_tasks(self):
        """Get list of available tasks from environment."""
        # This would interface with the environment
        # For now, return simulated tasks
        task_types = ['assembly', 'inspection', 'quality_control', 'material_handling']
        
        return [
            {
                'id': f"task_{i}",
                'type': random.choice(task_types),
                'priority': random.uniform(0.5, 1.0),
                'urgency': random.uniform(0.3, 1.0),
                'duration': random.randint(5, 15)
            }
            for i in range(random.randint(1, 3))
        ]

    async def setup(self):
        """Set up the robotic arm agent."""
        print(f"{self.agent_id}: Robotic arm agent started")
        await super().setup()

    async def on_start(self):
        """Handle agent start event."""
        print(f"{self.agent_id}: Robotic arm agent started")

    async def on_stop(self):
        """Handle agent stop event."""
        print(f"{self.agent_id}: Robotic arm agent stopped")

    # Material transfer protocol methods
    async def can_accept_transfer(self, material_id, quantity):
        """Check if robotic arm can accept a material transfer."""
        return (self.gripper_status == "open" and 
                len(self.task_queue) < 3)

    async def get_ready_time(self):
        """Get time when robotic arm is ready to receive materials."""
        return self.current_step + 3  # Ready in 3 time steps

    async def perform_transfer(self):
        """Perform a material transfer."""
        success = random.random() < self.precision_level
        return "success" if success else "failure"