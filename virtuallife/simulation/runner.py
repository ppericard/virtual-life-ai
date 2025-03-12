"""Simulation runner module for managing simulation execution.

This module provides the core simulation runner that controls the execution
of the simulation, including advancing the simulation state, managing entities,
and notifying listeners of events.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
import time
import logging
from uuid import UUID

from virtuallife.simulation.environment import Environment


# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class SimulationRunner:
    """Controls the simulation execution.

    The SimulationRunner class manages the execution of the simulation, including
    advancing the simulation state, managing entities, and notifying listeners
    of events.

    Attributes:
        environment: The environment for the simulation
        config: Configuration parameters
        current_step: The current simulation step
        running: Whether the simulation is currently running
        last_update_time: Timestamp of the last update
        listeners: Dictionary mapping event types to lists of callback functions

    Examples:
        >>> from unittest.mock import MagicMock
        >>> env = MagicMock()
        >>> sim = SimulationRunner(environment=env)
        >>> sim.current_step
        0
    """
    environment: Environment
    config: Dict[str, Any] = field(default_factory=dict)
    current_step: int = 0
    running: bool = False
    last_update_time: float = field(default_factory=time.time)
    listeners: Dict[str, List[Callable]] = field(default_factory=lambda: {
        "step_start": [],
        "step_end": [],
        "entity_added": [],
        "entity_removed": []
    })

    def add_listener(self, event_type: str, callback: Callable) -> None:
        """Add a listener for a specific event type.

        Args:
            event_type: The type of event to listen for
            callback: The function to call when the event occurs

        Raises:
            ValueError: If the event type is not supported

        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> sim = SimulationRunner(environment=env)
            >>> callback = lambda sim, **kwargs: None
            >>> sim.add_listener("step_start", callback)
            >>> len(sim.listeners["step_start"])
            1
        """
        if event_type not in self.listeners:
            raise ValueError(f"Unsupported event type: {event_type}")

        self.listeners[event_type].append(callback)

    def notify_listeners(self, event_type: str, **kwargs) -> None:
        """Notify all listeners of an event.

        Args:
            event_type: The type of event that occurred
            **kwargs: Additional data to pass to the listeners

        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> sim = SimulationRunner(environment=env)
            >>> data = {"called": False}
            >>> def callback(sim, **kwargs):
            ...     data["called"] = True
            >>> sim.add_listener("step_start", callback)
            >>> sim.notify_listeners("step_start")
            >>> data["called"]
            True
        """
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(self, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {event_type} listener: {str(e)}")

    def step(self) -> None:
        """Execute a single simulation step.

        This advances the simulation by one step, updating all entities
        and notifying listeners of the step start and end events.

        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> env.entities = {}
            >>> sim = SimulationRunner(environment=env)
            >>> sim.step()
            >>> sim.current_step
            1
        """
        try:
            self.notify_listeners("step_start")
            self.current_step += 1

            # Update all entities (make a copy to handle removals during iteration)
            entities = list(self.environment.entities.values())
            for entity in entities:
                try:
                    entity.update(self.environment)
                except Exception as e:
                    logger.error(f"Error updating entity {entity.id}: {str(e)}")

            self.notify_listeners("step_end")
        except Exception as e:
            logger.error(f"Error during simulation step {self.current_step}: {str(e)}")

    def run(self, steps: Optional[int] = None) -> None:
        """Run the simulation for a number of steps or indefinitely.

        Args:
            steps: Number of steps to run, or None to run indefinitely

        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> env.entities = {}
            >>> sim = SimulationRunner(environment=env)
            >>> # Run for 5 steps
            >>> sim.run(5)
            >>> sim.current_step
            5
        """
        self.running = True
        step_count = 0

        try:
            while self.running and (steps is None or step_count < steps):
                self.step()
                step_count += 1

                # Optional sleep for real-time visualization
                if "step_delay" in self.config:
                    time.sleep(self.config["step_delay"])
        except Exception as e:
            logger.error(f"Error during simulation run: {str(e)}")
        finally:
            self.running = False

    def stop(self) -> None:
        """Stop the simulation.

        Examples:
            >>> from unittest.mock import MagicMock
            >>> env = MagicMock()
            >>> sim = SimulationRunner(environment=env)
            >>> sim.running = True
            >>> sim.stop()
            >>> sim.running
            False
        """
        self.running = False 