class assert_value_equal:
    """Assert that two values are equal (supports variable rendering)"""

    def __init__(self, driver):
        self.driver = driver

    def assert_value_equal(self, **kwargs):
        expected = kwargs.get("expected", "")
        var_name = kwargs.get("var_name", "")
        actual = kwargs.get("actual", "")
        from webtest.tool.webrun.core.globalContext import g_context
        from webtest.tool.webrun.utils.VarRender import refresh
        all_ctx = g_context().show_dict()
        if var_name:
            actual = str(g_context().get_dict(var_name))
            actual = refresh(actual, all_ctx)
        elif actual:
            actual = str(actual)
        else:
            raise ValueError("Provide 'var_name' or 'actual' parameter")
        expected = refresh(str(expected), all_ctx)
        if expected.strip() != actual.strip():
            raise AssertionError(f"Value mismatch: expected '{expected}' != actual '{actual}'")
        print(f"[Assert] Values equal: '{expected}'")