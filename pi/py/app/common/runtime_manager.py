import asyncio, threading
from common import singleton_decorator as s
from typing import Callable, Coroutine, Optional
import logging

@s.singleton
class RuntimeManager:
    """Class to manage async runtime so that async functions can be called from a sync context (like a Dash callback). Is a singleton, so the same runtime is used for all async operations.
    """
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.loop = asyncio.new_event_loop()
            self.initialized = True
            
            # Start the event loop in a background thread
            thread = threading.Thread(target=self._start_loop, daemon=True)
            thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def add_task(self, coro: Coroutine, cb: Optional[Callable]=None):
        """Adds an asynchronous task to the runtime manager with a possible callback for when it finishes. 

        Args:
            coro (Coroutine): Return value of the async function to execute.
            cb (Callable, optional): Callback that will be called when the task completes. If there is a return value, it will be passed into the callback. Defaults to None.

        Raises:
            e (Exception): If the task fails.
        """        
        def task_done_callback(fut: asyncio.Future):
            try:
                result = fut.result() 
                cb(result)
            except Exception as e:
                logging.error(f"[RTM] Callback for {fut} failed with {e.__class__} error: {e}")
                raise e

        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        if cb:
            future.add_done_callback(task_done_callback)
        
    def __del__(self):
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)