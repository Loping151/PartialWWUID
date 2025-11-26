import asyncio
import threading
from typing import Any, Callable, Coroutine, Dict, List, Union

from gsuid_core.logger import logger


class TaskDispatcher:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        self.handlers: Dict[str, List[Callable]] = {}

    def register_handler(
        self,
        task_type: str,
        handler: Callable[[Any], Union[Any, Coroutine[Any, Any, Any]]],
    ) -> None:
        # 初始化处理器列表
        if task_type not in self.handlers:
            self.handlers[task_type] = []

        # 添加处理器到列表
        self.handlers[task_type].append(handler)
        logger.info(f"注册任务处理器: {task_type} -> {handler.__name__}")

    def emit(self, task_type: str, data: Any) -> None:
        if not self.running:
            logger.warning("任务分发器未启动或已关闭")
            return
        if task_type not in self.handlers:
            return

        try:
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(self.queue.put((task_type, data)), loop)
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.queue.put((task_type, data)))

    async def _process(self) -> None:
        while True:
            try:
                if not self.running:
                    break

                task_type, data = await asyncio.wait_for(self.queue.get(), timeout=3.0)

                # 获取所有处理器并依次执行
                handlers = self.handlers.get(task_type, [])
                for handler in handlers:
                    asyncio.create_task(self._run_task(handler, data, task_type))

                self.queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.exception(f"任务处理异常: {e}")

    async def _run_task(self, handler: Callable, data: Any, task_type: str) -> None:
        try:
            result = handler(data)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.exception(f"任务执行错误 ({task_type}): {e}")

    def start(self, daemon: bool = True) -> None:
        if self.running:
            return

        self.running = True
        threading.Thread(
            target=lambda: asyncio.run(self._process()), daemon=daemon
        ).start()


# 创建全局任务分发器实例
dispatcher = TaskDispatcher()


def register_handler(
    task_type: str,
    handler: Callable[[Any], Union[Any, Coroutine[Any, Any, Any]]],
) -> None:
    dispatcher.register_handler(task_type, handler)


def start_dispatcher(daemon: bool = True) -> None:
    dispatcher.start(daemon=daemon)


def push_item(queue_name: str, item: Any) -> None:
    dispatcher.emit(queue_name, item)


def event_handler(task_type: str) -> Callable:
    """
    事件处理器装饰器, 用于本地撰写排行等逻辑，不干扰主库代码；

    Examples:
        放在 __init__.py 中, 让gsuid_core自动注册到任务分发器中

        @event_handler("score_rank")
        async def handle_score_rank(data):
            print(f"处理评分数据: {data}")

        @event_handler("score_rank")
        def handle_score_rank_log(data):
            print(f"记录评分数据: {data}")
    """

    def decorator(func: Callable) -> Callable:
        # 注册处理器
        dispatcher.register_handler(task_type, func)
        return func

    return decorator
