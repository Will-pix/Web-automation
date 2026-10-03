class api_get_request:
    """Send HTTP GET request and store response in variable"""

    def __init__(self, driver):
        self.driver = driver

    def api_get_request(self, **kwargs):
        import requests
        import json as json_mod
        url = kwargs.get("url", "")
        var_name = kwargs.get("var_name", "api_response")
        headers_str = kwargs.get("headers", "{}")
        if not url:
            raise ValueError("Parameter 'url' is required")
        from webtest.tool.webrun.core.globalContext import g_context
        from webtest.tool.webrun.utils.VarRender import refresh
        all_ctx = g_context().show_dict()
        url = refresh(url, all_ctx)
        try:
            headers = json_mod.loads(headers_str)
        except Exception:
            headers = {"Content-Type": "application/json"}
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = resp.text
                g_context().set_dict(var_name, data)
                print(f"[API] GET {url} -> status={resp.status_code}, stored in '{var_name}'")
                return
            except requests.RequestException as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise RuntimeError(f"API GET failed: {url}, error: {e}")

import time