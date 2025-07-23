import asyncio
from typing import Callable, Awaitable
import inspect

class Job:
    def __init__(self, delay: int, callback: Callable[[], Awaitable[None]]):
        if not inspect.iscoroutinefunction(callback):
            raise TypeError("The job callback must be a coroutine (using async def).")

        self.delay = delay
        self.callback = callback
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        """
        Asynchronously runs the job after a specified delay and executes the callback.
    
        Sleeps for the specified delay before calling the asynchronous callback function.
        If the task is cancelled, handles the asyncio.CancelledError exception gracefully.
        """

        try:
            await asyncio.sleep(self.delay)
            await self.callback()
        except asyncio.CancelledError:
            pass

    def cancel(self):
        """
        Cancels the job if it has not yet completed.

        If the job task is not done, this method cancels the task to prevent it from running.
        If the task has already completed, this method does nothing.
        """

        if self._task and not self._task.done():
            self._task.cancel()