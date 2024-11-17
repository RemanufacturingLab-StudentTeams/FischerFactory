import asyncio, threading
from common import singleton_decorator as s
from typing import Callable, Coroutine
from common import server
import logging

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
                
    def add_task(self, coro: Coroutine, cb: Callable=None, ws_endpoint: str=None):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
    
        def handle_result(fut):
            logging.info(fut)
            try:
                result = fut.result()
                
                if ws_endpoint:
                    logging.debug('emitting: ' + str(result))
                    server.socketio.emit('message', {'message': str(result)}, namespace='/' + ws_endpoint)
                
                if cb:
                    cb(result)  
            except Exception as e:
                logging.error(f"[RTM] Task failed with exception: {e}")
        
        future.add_done_callback(handle_result)
        
    def __del__(self):
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)