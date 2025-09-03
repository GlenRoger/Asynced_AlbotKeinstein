import asyncio
import logging
import time
from enum import Enum
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass


class TaskState(Enum):
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    RESTARTING = "restarting"
    STOPPED = "stopped"
    SHUTDOWN = "shutdown"


class RestartPolicy(Enum):
    ALWAYS = "always"
    NEVER = "never"
    CONDITIONAL = "conditional"
    MAX_ATTEMPTS = "max_attempts"


@dataclass
class TaskMetadata:
    """Stores information about a managed task"""
    name: str
    task_func: Callable
    restart_policy: RestartPolicy
    max_retries: int = 10
    
    # Runtime data
    task: Optional[asyncio.Task] = None
    state: TaskState = TaskState.STOPPED
    start_time: Optional[float] = None
    restart_count: int = 0
    last_failure: Optional[str] = None
    last_failure_time: Optional[float] = None


class TaskSupervisor:
    """
    Monitors and manages asyncio tasks with automatic restart capabilities.
    Provides centralized task management and status reporting.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        print("init started!")
        # self.logger = logger or logging.getLogger(__name__)
        # self.logger_prefix = "utils/TaskSupervisor=>"
        
        # Task registry
        self.tasks: Dict[str, TaskMetadata] = {}
        
        # Supervisor control
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.monitor_interval = 2.0  # seconds between health checks
        
        # self.logger.info(f"{self.logger_prefix}TaskSupervisor initialized")

    def register_task(self, name: str, task_fun: Callable, restart_policy: RestartPolicy = RestartPolicy.ALWAYS, max_retries: int = 10) -> None:
        print(f"Cought this {name}")

    # def register_task(self, name: str, task_func: Callable, 
    #                  restart_policy: RestartPolicy = RestartPolicy.ALWAYS,
    #                  max_retries: int = 10) -> None:
    #     """Register a task for supervision"""
    #     # TODO: Implement task registration
    #     pass
    
    async def start_monitoring(self) -> None:
        """Start the supervisor monitoring loop"""
        # TODO: Implement monitoring startup
        pass
    
    # async def stop_monitoring(self) -> None:
    #     """Stop the supervisor and all managed tasks"""
    #     # TODO: Implement graceful shutdown
    #     pass
    
    # async def _monitor_loop(self) -> None:
    #     """Main monitoring loop - checks task health periodically"""
    #     # TODO: Implement main monitoring logic
    #     pass
    
    # async def _check_task_health(self) -> None:
    #     """Check health of all registered tasks"""
    #     # TODO: Implement health checking logic
    #     pass
    
    # async def _handle_failed_task(self, task_meta: TaskMetadata) -> None:
    #     """Handle a task that has failed or completed unexpectedly"""
    #     # TODO: Implement failure handling and restart logic
    #     pass
    
    async def _start_task(self, task_meta: TaskMetadata) -> bool:
        """Start or restart a specific task"""
        # TODO: Implement task starting logic
        pass
    
    # async def _calculate_restart_delay(self, task_meta: TaskMetadata) -> float:
    #     """Calculate delay before restart using squared backoff"""
    #     # TODO: Implement your squared backoff algorithm
    #     pass
    
    # async def restart_task(self, name: str) -> bool:
    #     """Manually restart a specific task"""
    #     # TODO: Implement manual restart functionality
    #     pass
    
    # async def stop_task(self, name: str) -> bool:
    #     """Stop a specific task gracefully"""
    #     # TODO: Implement task stopping logic
    #     pass
    
    # def get_task_status(self, name: Optional[str] = None) -> Dict[str, Any]:
    #     """Get status information for tasks (specific task or all tasks)"""
    #     # TODO: Implement status reporting
    #     pass
    
    # def get_all_tasks_summary(self) -> Dict[str, Any]:
    #     """Get summary status of all tasks for dashboard"""
    #     # TODO: Implement summary status for dashboard
    #     pass


# ========================================
# TESTING FRAMEWORK
# ========================================

class MockTasks:
    """Mock task functions for testing the supervisor"""

    @staticmethod
    async def task_running_minutes_1() -> None:
        print(f"HI!! Nerd")
        await asyncio.sleep(15)
        print(f"BYE!! Nerd")

    @staticmethod
    async def task_running_minutes_2() -> None:
        print(f"HI!! Turd")
        await asyncio.sleep(20)
        print(f"BYE!! Turd")

    @staticmethod
    async def task_running_minutes_3() -> None:
        print(f"HI!! Third")
        await asyncio.sleep(10)
        print(f"BYE!! Third")


   
#     async def stable_task(duration: int = 5) -> None:
#         """A task that runs for specified duration then completes normally"""
#         # TODO: Implement stable test task
#         pass
    
#     @staticmethod
#     async def crash_task(crash_after: int = 2) -> None:
#         """A task that crashes after specified time"""
#         # TODO: Implement crashing test task
#         pass
    
#     @staticmethod
#     async def random_failure_task(failure_chance: float = 0.3) -> None:
#         """A task that randomly fails"""
#         # TODO: Implement random failure test task
#         pass
    
#     @staticmethod
#     async def infinite_task() -> None:
#         """A task that runs until cancelled (like real bot tasks)"""
#         # TODO: Implement infinite test task
#         pass


async def run_supervisor_tests():
    """Run comprehensive tests of the TaskSupervisor"""
    print()
    print("=" * 50)
    print("TASK SUPERVISOR TESTING")
    print("=" * 50)

    task_supervisor = TaskSupervisor()

    # await task_running_minutes(100)
    # await task_running_minutes(50)
    # await task_running_minutes(45)

    # Run concurrently
    # tasks = [
    #     asyncio.create_task(task_running_minutes(10, "Howdy!")),
    #     asyncio.create_task(task_running_minutes(50, "Rowdy!")),
    #     asyncio.create_task(task_running_minutes(45, "Loudly!"))
    # ]
    # await asyncio.gather(*tasks)  # Wait for all to complete


    task_supervisor.register_task("Task_1", MockTasks.task_running_minutes_1)
    task_supervisor.register_task("Task_2", MockTasks.task_running_minutes_2)
    task_supervisor.register_task("Task_3", MockTasks.task_running_minutes_3)

    await task_supervisor.start_monitoring()


    # Setup logging for tests
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     logger = logging.getLogger("TaskSupervisorTest")
    
#     # TODO: Implement test scenarios
#     # Test 1: Basic task registration and monitoring
#     # Test 2: Task failure and restart
#     # Test 3: Multiple task management
#     # Test 4: Restart policies
#     # Test 5: Maximum retry limits
#     # Test 6: Manual task control
#     # Test 7: Graceful shutdown
    
#     print("\n" + "=" * 50)
#     print("ALL TESTS COMPLETED")
#     print("=" * 50)


if __name__ == "__main__":
    """Run standalone tests when executed directly"""
    asyncio.run(run_supervisor_tests())
