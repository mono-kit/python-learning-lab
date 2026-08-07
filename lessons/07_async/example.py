"""asyncio 协程和结构化并发。"""

import asyncio


async def fetch_user(user_id: int, delay: float = 0.01) -> dict[str, object]:
    """sleep 模拟非阻塞 I/O；await 暂停当前协程，让出执行权。"""
    await asyncio.sleep(delay)
    return {"id": user_id, "name": f"user-{user_id}"}


async def fetch_users(user_ids: list[int]) -> list[dict[str, object]]:
    """TaskGroup 保证所有子任务完成，或在失败时统一取消。"""
    tasks: list[asyncio.Task[dict[str, object]]] = []
    async with asyncio.TaskGroup() as group:
        for user_id in user_ids:
            tasks.append(group.create_task(fetch_user(user_id)))
    return [task.result() for task in tasks]


async def ticker(count: int):
    """async generator 可以通过 async for 消费。"""
    for number in range(count):
        await asyncio.sleep(0)
        yield number


async def main() -> None:
    print(await fetch_users([1, 2, 3]))
    async for number in ticker(3):
        print(number)


if __name__ == "__main__":
    asyncio.run(main())
