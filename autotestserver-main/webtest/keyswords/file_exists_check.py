class file_exists_check:
    """Check if a file exists and store result in variable"""

    def __init__(self, driver):
        self.driver = driver

    def file_exists_check(self, **kwargs):
        import os
        file_path = kwargs.get("file_path", "")
        var_name = kwargs.get("var_name", "file_exists")
        if not file_path:
            raise ValueError("Parameter 'file_path' is required")
        if not os.path.isabs(file_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            from app import application
            upload_dir = application.config.get('UPLOAD_FOLDER', '../file')
            file_path = os.path.abspath(os.path.join(current_dir, upload_dir, file_path))
        exists = os.path.exists(file_path) and os.path.isfile(file_path)
        from webtest.tool.webrun.core.globalContext import g_context
        g_context().set_dict(var_name, "true" if exists else "false")
        print(f"[File] {file_path} exists: {exists}")