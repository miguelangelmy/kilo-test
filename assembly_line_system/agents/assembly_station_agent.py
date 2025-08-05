"""
Assembly Station Agent implementation for the assembly line system.
"""

from assembly_line_system.agents.base_agent import AssemblyLineAgent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
import json
import random

class AssemblyStationAgent(AssemblyLineAgent):
    """
    Agent representing an assembly station in the assembly line.

    Responsibilities:
    - Complete final product assembly from components
    - Quality assurance and testing of assembled products
    - Packaging and preparation for shipping
    - Production optimization and efficiency monitoring
    """

    def __init__(self, agent_id, jid, password, env):
        """
        Initialize the assembly station agent.

        Args:
            agent_id (str): Unique identifier for the agent
            jid (str): JID for XMPP communication
            password (str): Password for XMPP authentication
            env: Reference to the shared environment
        """
        super().__init__(agent_id, jid, password, env)

        # Assembly station-specific attributes
        self.assembly_capacity = 3  # Maximum simultaneous assemblies
        self.current_assemblies = []
        self.production_rate = 1.0  # Products per time step
        self.quality_threshold = 0.85  # Minimum quality for passing
        self.station_efficiency = random.uniform(0.8, 1.0)
        self.maintenance_status = "operational"  # operational, maintenance, calibration
        self.total_assemblies_completed = 0
        self.defect_rate = 0.05  # Initial defect rate
        
    def _setup_cyclic_behaviour(self):
        """Set up cyclic behavior for continuous operation."""
        class AssemblyStationCyclicBehaviour(CyclicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Assembly station cyclic behaviour running")

                # Check maintenance status
                if self.maintenance_status == "operational":
                    # Process current assemblies
                    await self._process_assemblies()
                    
                    # Look for new components to assemble
                    await self._scan_for_components()
                    
                    # Quality control on completed assemblies
                    await self._perform_quality_control()
                else:
                    print(f"{self.agent_id}: Station in {self.maintenance_status} status")

        return AssemblyStationCyclicBehaviour()

    def _setup_periodic_behaviour(self):
        """Set up periodic behavior for regular tasks."""
        class AssemblyStationPeriodicBehaviour(PeriodicBehaviour):
            async def run(self):
                print(f"{self.agent_id}: Assembly station periodic behaviour running")

                # Check maintenance needs
                await self._check_maintenance()
                
                # Optimize production parameters
                await self._optimize_production()
                
                # Update station efficiency based on performance
                await self._update_efficiency()

        return AssemblyStationPeriodicBehaviour(period=12)  # Check every 12 time steps

    async def _process_assemblies(self):
        """Process current assemblies in progress."""
        print(f"{self.agent_id}: Processing {len(self.current_assemblies)} assemblies")
        
        completed_assemblies = []
        
        for assembly in self.current_assemblies[:]:  # Copy list to avoid modification during iteration
            # Update assembly progress
            progress_increment = self.production_rate * self.station_efficiency * 0.1
            assembly['progress'] = min(1.0, assembly.get('progress', 0) + progress_increment)
            
            print(f"{self.agent_id}: Assembly {assembly['id']} progress: {assembly['progress']:.2f}")
            
            # Check if assembly is complete
            if assembly['progress'] >= 1.0:
                completed_assemblies.append(assembly)
                
        # Remove completed assemblies
        for assembly in completed_assemblies:
            self.current_assemblies.remove(assembly)
            await self._complete_assembly(assembly)

    async def _scan_for_components(self):
        """Scan for available components to start new assemblies."""
        print(f"{self.agent_id}: Scanning for components")
        
        # Check if we have capacity for new assemblies
        if len(self.current_assemblies) < self.assembly_capacity:
            available_components = self._get_available_components()
            
            if available_components and len(available_components) >= 3:  # Need at least 3 components
                # Start a new assembly
                await self._start_new_assembly(available_components)

    async def _perform_quality_control(self):
        """Perform quality control on completed assemblies."""
        print(f"{self.agent_id}: Performing quality control")
        
        # Check recent assemblies for quality issues
        for assembly in self.current_assemblies:
            if (assembly.get('progress', 0) > 0.8 and 
                'quality_score' not in assembly):
                
                # Assess quality based on component quality and assembly precision
                base_quality = sum(c.get('quality', 0.8) for c in assembly.get('components', [])) / len(assembly.get('components', []))
                precision_factor = self.station_efficiency
                quality_score = base_quality * precision_factor
                
                assembly['quality_score'] = quality_score
                
                print(f"{self.agent_id}: Assembly {assembly['id']} quality: {quality_score:.2f}")

    async def _start_new_assembly(self, components):
        """Start a new assembly with available components."""
        print(f"{self.agent_id}: Starting new assembly")
        
        # Create new assembly
        assembly_id = f"assembly_{self.total_assemblies_completed + 1}"
        
        new_assembly = {
            'id': assembly_id,
            'components': components[:3],  # Use first 3 components
            'progress': 0.0,
            'start_time': self.current_step,
            'estimated_duration': random.randint(8, 15),
            'quality_score': None
        }
        
        self.current_assemblies.append(new_assembly)
        print(f"{self.agent_id}: Started assembly {assembly_id} with {len(components)} components")

    async def _complete_assembly(self, assembly):
        """Complete a finished assembly."""
        print(f"{self.agent_id}: Completing assembly {assembly['id']}")
        
        # Calculate final metrics
        duration = self.current_step - assembly.get('start_time', 0)
        quality_score = assembly.get('quality_score', random.uniform(0.7, 1.0))
        
        # Determine if assembly passes quality control
        passes_qc = quality_score >= self.quality_threshold
        
        if passes_qc:
            # Successful completion
            self.total_assemblies_completed += 1
            
            # Calculate efficiency bonus
            efficiency_bonus = (assembly.get('estimated_duration', 10) / duration) * self.station_efficiency
            quality_bonus = quality_score
            
            total_reward = efficiency_bonus + quality_bonus
            print(f"{self.agent_id}: Assembly completed successfully! Reward: {total_reward:.2f}")
            
            # Update defect rate based on quality
            if quality_score < 0.9:
                self.defect_rate = min(0.2, self.defect_rate + 0.01)
            else:
                self.defect_rate = max(0.01, self.defect_rate - 0.005)
                
        else:
            # Assembly failed quality control
            print(f"{self.agent_id}: Assembly failed quality control (score: {quality_score:.2f})")
            
            # Penalty for defect
            penalty = -1.0 * quality_score
            print(f"{self.agent_id}: Quality penalty: {penalty:.2f}")
            
            # Update defect rate
            self.defect_rate = min(0.2, self.defect_rate + 0.02)

    async def _check_maintenance(self):
        """Check if assembly station needs maintenance."""
        print(f"{self.agent_id}: Checking maintenance status")
        
        # Check based on production volume
        if self.total_assemblies_completed >= 50 and random.random() < 0.3:
            self.maintenance_status = "maintenance"
            print(f"{self.agent_id}: Station needs maintenance")
            
        # Check for random failures
        elif self.maintenance_status == "operational" and random.random() < 0.02:
            self.maintenance_status = "calibration"
            print(f"{self.agent_id}: Station needs calibration")
            
        # Check for recovery
        elif self.maintenance_status in ["maintenance", "calibration"] and random.random() < 0.4:
            self.maintenance_status = "operational"
            print(f"{self.agent_id}: Station back to operational")

    async def _optimize_production(self):
        """Optimize production parameters."""
        print(f"{self.agent_id}: Optimizing production")
        
        # Adjust production rate based on current conditions
        if len(self.current_assemblies) == 0:
            # No assemblies, increase production rate
            self.production_rate = min(2.0, self.production_rate + 0.1)
        elif len(self.current_assemblies) >= self.assembly_capacity:
            # At capacity, decrease production rate for quality
            self.production_rate = max(0.5, self.production_rate - 0.05)
            
        # Adjust quality threshold based on defect rate
        if self.defect_rate > 0.1:
            # High defect rate, be more strict
            self.quality_threshold = min(0.95, self.quality_threshold + 0.02)
        elif self.defect_rate < 0.03:
            # Low defect rate, can be more efficient
            self.quality_threshold = max(0.75, self.quality_threshold - 0.01)
            
        print(f"{self.agent_id}: Production rate: {self.production_rate:.2f}, Quality threshold: {self.quality_threshold:.2f}")

    async def _update_efficiency(self):
        """Update station efficiency based on performance."""
        print(f"{self.agent_id}: Updating efficiency")
        
        # Calculate efficiency based on completion rate and quality
        completion_rate = self.total_assemblies_completed / max(1, self.current_step)
        quality_factor = 1.0 - self.defect_rate
        
        target_efficiency = completion_rate * quality_factor
        
        # Gradually adjust towards target
        self.station_efficiency += (target_efficiency - self.station_efficiency) * 0.1
        
        # Keep efficiency in valid range
        self.station_efficiency = max(0.5, min(1.0, self.station_efficiency))
        
        print(f"{self.agent_id}: Station efficiency: {self.station_efficiency:.3f}")

    def _get_available_components(self):
        """Get list of available components from environment."""
        # This would interface with the environment
        # For now, return simulated components
        component_types = ['component_A', 'component_B', 'component_C', 'fastener', 'electronic_part']
        
        return [
            {
                'id': f"comp_{i}",
                'type': random.choice(component_types),
                'quality': random.uniform(0.7, 1.0)
            }
            for i in range(random.randint(3, 6))
        ]

    async def setup(self):
        """Set up the assembly station agent."""
        print(f"{self.agent_id}: Assembly station agent started")
        await super().setup()

    async def on_start(self):
        """Handle agent start event."""
        print(f"{self.agent_id}: Assembly station agent started")

    async def on_stop(self):
        """Handle agent stop event."""
        print(f"{self.agent_id}: Assembly station agent stopped")

    # Material transfer protocol methods
    async def can_accept_transfer(self, material_id, quantity):
        """Check if assembly station can accept a material transfer."""
        return (self.maintenance_status == "operational" and 
                len(self.current_assemblies) < self.assembly_capacity)

    async def get_ready_time(self):
        """Get time when assembly station is ready to receive materials."""
        return self.current_step + 2  # Ready in 2 time steps

    async def perform_transfer(self):
        """Perform a material transfer."""
        success = random.random() < (0.9 * self.station_efficiency)
        return "success" if success else "failure"

    # Statistics and monitoring methods
    def get_production_stats(self):
        """Get current production statistics."""
        return {
            'total_assemblies': self.total_assemblies_completed,
            'current_assemblies': len(self.current_assemblies),
            'defect_rate': self.defect_rate,
            'station_efficiency': self.station_efficiency,
            'production_rate': self.production_rate
        }

    def get_assembly_status(self):
        """Get status of current assemblies."""
        return [
            {
                'id': assembly['id'],
                'progress': assembly.get('progress', 0),
                'quality_score': assembly.get('quality_score'),
                'duration': self.current_step - assembly.get('start_time', 0)
            }
            for assembly in self.current_assemblies
        ]