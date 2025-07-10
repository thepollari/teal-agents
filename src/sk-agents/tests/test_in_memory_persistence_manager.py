import asyncio

import pytest

from src.sk_agents.exceptions import PersistenceCreateError
from src.sk_agents.persistence.in_memory_persistence_manager import (
    AgentTask,
    InMemoryPersistenceManager,
)


@pytest.fixture
def persistence_manager():
    """Provides a fresh InMemoryPersistenceManager for each test."""
    yield InMemoryPersistenceManager()


@pytest.fixture
def task_a():
    """Provides a sample AgentTask for testing."""
    return AgentTask(task_id="task-id-1", task="agent task 1")


@pytest.fixture
def task_b():
    """Provides another sample AgentTask for testing."""
    return AgentTask(task_id="task-id-2", task="agent task 2")


@pytest.mark.asyncio
async def test_create_and_load_task(persistence_manager, task_a):
    """Test creating a task and then loading it successfully."""
    await persistence_manager.create(task_a)
    loaded_task = await persistence_manager.load(task_a.task_id)
    assert loaded_task == task_a


@pytest.mark.asyncio
async def test_load_non_existent_task(persistence_manager):
    """Test loading a task that does not exist should raise ValueError."""
    with pytest.raises(ValueError, match="Task with ID 'non_existent_id' not found."):
        await persistence_manager.load("non_existent_id")


@pytest.mark.asyncio
async def test_create_duplicate_task(persistence_manager, task_a):
    """Test creating a task with an ID that already exists should raise PersistenceCreateError."""
    await persistence_manager.create(task_a)
    with pytest.raises(PersistenceCreateError):
        await persistence_manager.create(task_a)


@pytest.mark.asyncio
async def test_update_existing_task(persistence_manager, task_a):
    """Test updating an existing task successfully."""
    await persistence_manager.create(task_a)
    updated_task = AgentTask(task_id=task_a.task_id, task="agent task update")
    await persistence_manager.update(updated_task)
    loaded_task = await persistence_manager.load(task_a.task_id)
    assert loaded_task == updated_task


@pytest.mark.asyncio
async def test_update_non_existent_task(persistence_manager, task_b):
    """Test updating a task that does not exist should raise ValueError."""
    with pytest.raises(
        ValueError, match=f"Task with ID '{task_b.task_id}' does not exist for update."
    ):
        await persistence_manager.update(task_b)


@pytest.mark.asyncio
async def test_delete_existing_task(persistence_manager, task_a):
    """Test deleting an existing task successfully."""
    await persistence_manager.create(task_a)
    await persistence_manager.delete(task_a.task_id)
    with pytest.raises(ValueError, match=f"Task with ID '{task_a.task_id}' not found."):
        await persistence_manager.load(task_a.task_id)


@pytest.mark.asyncio
async def test_delete_non_existent_task(persistence_manager):
    """Test deleting a task that does not exist should raise ValueError."""
    with pytest.raises(
        ValueError, match="Task with ID 'non_existent_id' does not exist for deletion."
    ):
        await persistence_manager.delete("non_existent_id")


@pytest.mark.asyncio
async def test_concurrent_create(persistence_manager):
    """Test that concurrent create operations are handled correctly by the lock."""
    tasks_to_create = [AgentTask(task_id=f"task-id-{_}", task=f"task {_}") for _ in range(100)]

    async def create_task_wrapper(task):
        await persistence_manager.create(task)

    await asyncio.gather(*[create_task_wrapper(task) for task in tasks_to_create])

    # Verify all tasks were created and no duplicates (by ID)
    assert len(persistence_manager.in_memory) == len(tasks_to_create)
    for task in tasks_to_create:
        loaded_task = await persistence_manager.load(task.task_id)
        assert loaded_task == task


@pytest.mark.asyncio
async def test_concurrent_update(persistence_manager):
    """Test that concurrent update operations are handled correctly by the lock."""
    original_tasks = [AgentTask(task_id=f"task-id-{_}", task=f"task {_}") for _ in range(50)]
    for task in original_tasks:
        await persistence_manager.create(task)

    # Prepare updated tasks with new data
    updated_tasks_data = {
        task.task_id: f"Updated for task {i}" for i, task in enumerate(original_tasks)
    }

    async def update_task_wrapper(task_id, data):
        updated_task = AgentTask(task_id=task_id, task=data)
        await persistence_manager.update(updated_task)

    await asyncio.gather(
        *[
            update_task_wrapper(task.task_id, updated_tasks_data[task.task_id])
            for task in original_tasks
        ]
    )

    # Verify all tasks were updated to their final state
    for task in original_tasks:
        loaded_task = await persistence_manager.load(task.task_id)
        assert loaded_task.task == updated_tasks_data[task.task_id]


@pytest.mark.asyncio
async def test_concurrent_mixed_operations(persistence_manager):
    """Test mixed concurrent operations (create, update, delete, load)."""
    initial_tasks = [AgentTask(task_id=f"task-id-{_}", task=f"task {_}") for _ in range(20)]
    for task in initial_tasks:
        await persistence_manager.create(task)

    tasks_to_delete = initial_tasks[0:5]
    tasks_to_update = initial_tasks[5:10]
    tasks_to_load = initial_tasks[10:15]
    tasks_to_create_new = [
        AgentTask(task_id=f"task-id-{_}", task=f"task {_}") for _ in range(20, 25)
    ]

    async def run_operations():
        # Create new
        create_coros = [persistence_manager.create(t) for t in tasks_to_create_new]
        # Update existing
        update_coros = [
            persistence_manager.update(AgentTask(task_id=t.task_id, task="Concurrently Updated"))
            for t in tasks_to_update
        ]
        # Delete existing
        delete_coros = [persistence_manager.delete(t.task_id) for t in tasks_to_delete]
        # Load existing
        load_coros = [persistence_manager.load(t.task_id) for t in tasks_to_load]

        await asyncio.gather(
            *create_coros,
            *update_coros,
            *delete_coros,
            *load_coros,
            return_exceptions=True,  # Allow other tasks to run if one fails
        )

    await run_operations()

    # Verify state after concurrent operations
    for task in tasks_to_create_new:
        loaded = await persistence_manager.load(task.task_id)
        assert loaded.task_id == task.task_id
    for task in tasks_to_update:
        loaded = await persistence_manager.load(task.task_id)
        assert loaded.task == "Concurrently Updated"
    for task in tasks_to_delete:
        with pytest.raises(ValueError):  # Should be deleted
            await persistence_manager.load(task.task_id)
    for task in tasks_to_load:
        assert await persistence_manager.load(task.task_id) is not None
