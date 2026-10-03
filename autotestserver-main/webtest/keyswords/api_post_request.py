class api_post_request:
    """Send HTTP POST request and store response in variable"""

    def __init__(self, driver):
        self.driver = driver

    def api_post_request(self, **kwargs):
        import requests
        import json as json_mod
        url = kwargs.get("url", "")
        body_str = kwargs.get("body", "{}")
        var_name = kwargs.get("var_name", "api_response")
        headers_str = kwargs.get("headers", '{"Content-Type":"application/json"}')
        if not url:
            raise ValueError("Parameter 'url' is required")
        from webtest.tool.webrun.core.globalContext import g_context
        from webtest.tool.webrun.utils.VarRender import refresh
        all_ctx = g_context().show_dict()
        url = refresh(url, all_ctx)
        body_str = refresh(body_str, all_ctx)
        try:
            headers = json_mod.loads(headers_str)
        except Exception:
            headers = {"Content-Type": "application/json"}
        try:
            body = json_mod.loads(body_str)
        except Exception:
            body = body_str
        for attempt in range(3):
            try:
                if isinstance(body, dict):
                    resp = requests.post(url, json=body, headers=headers, timeout=30)
                else:
                    resp = requests.post(url, data=body_str, headers=headers, timeout=30)
                resp.raise_for_status()
                try:
                    data = resp.json()
                except Exception:
                    data = resp.text
                g_context().set_dict(var_name, data)
                print(f"[API] POST {url} -> status={resp.status_code}, stored in '{var_name}'")
                return
            except requests.RequestException as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise RuntimeError(f"API POST failed: {url}, error: {e}")

import time