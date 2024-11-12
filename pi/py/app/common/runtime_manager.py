import asyncio, threading
from common import singleton_decorator as s
from typing import Callable

@s.singleton
class RuntimeManager:
    
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
                
    def add_task(self, coro: asyncio.coroutine, cb: Callable=None):
        if cb:
            asyncio.run_coroutine_threadsafe(coro, self.loop).add_done_callback(cb)
        else:
            asyncio.run_coroutine_threadsafe(coro, self.loop)
        
    def __del__(self):
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)