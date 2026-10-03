class wait_fixed_seconds:
    """Fixed time wait - use only when explicit waits are not applicable"""

    def __init__(self, driver):
        self.driver = driver

    def wait_fixed_seconds(self, **kwargs):
        seconds = float(kwargs.get("seconds", 1))
        if seconds > 60:
            print(f"[Wait] Warning: long fixed wait ({seconds}s), consider using explicit waits")
        time.sleep(seconds)
        print(f"[Wait] Fixed wait {seconds}s completed")

import time