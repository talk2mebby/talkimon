import threading

class TimeoutException(Exception):
    pass

def run_with_timeout(func, args=(), kwargs={}, timeout_sec=2):
    result = {}
    def target():
        try:
            result['value'] = func(*args, **kwargs)
        except Exception as e:
            result['error'] = e
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout_sec)
    if thread.is_alive():
        raise TimeoutException(f"Action timed out after {timeout_sec} seconds")
    if 'error' in result:
        raise result['error']
    return result.get('value', None)
