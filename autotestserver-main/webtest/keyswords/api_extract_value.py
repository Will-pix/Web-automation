class api_extract_value:
    """Extract value from API response JSON by path and store in variable"""

    def __init__(self, driver):
        self.driver = driver

    def api_extract_value(self, **kwargs):
        source_var = kwargs.get("source_var", "")
        json_path = kwargs.get("json_path", "")
        target_var = kwargs.get("target_var", "extracted")
        if not source_var or not json_path:
            raise ValueError("Parameters 'source_var' and 'json_path' are required")
        from webtest.tool.webrun.core.globalContext import g_context
        data = g_context().get_dict(source_var)
        if data is None:
            raise ValueError(f"Source variable '{source_var}' not found")
        parts = json_path.split(".")
        val = data
        for p in parts:
            try:
                if p.isdigit():
                    val = val[int(p)]
                else:
                    val = val[p]
            except (KeyError, IndexError, TypeError):
                val = None
                break
        g_context().set_dict(target_var, val)
        print(f"[API Extract] {source_var}{json_path} = {val} -> '{target_var}'")