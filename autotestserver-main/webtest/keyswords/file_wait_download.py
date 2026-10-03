class file_wait_download:
    """Wait for a file to finish downloading by monitoring the download directory"""

    def __init__(self, driver):
        self.driver = driver

    def file_wait_download(self, **kwargs):
        import os
        download_dir = kwargs.get("download_dir", os.path.expanduser("~/Downloads"))
        pattern = kwargs.get("filename_pattern", "*")
        timeout = int(kwargs.get("timeout", 60))
        var_name = kwargs.get("var_name", "downloaded_file")
        if not os.path.exists(download_dir):
            raise FileNotFoundError(f"Download directory not found: {download_dir}")
        before = set(os.listdir(download_dir))
        waited = 0
        while waited < timeout:
            time.sleep(2)
            waited += 2
            after = set(os.listdir(download_dir))
            new_files = after - before
            for f in new_files:
                if f.endswith(('.crdownload', '.tmp', '.part')):
                    continue
                import fnmatch
                if fnmatch.fnmatch(f, pattern):
                    filepath = os.path.join(download_dir, f)
                    time.sleep(1)
                    if os.path.getsize(filepath) > 0:
                        from webtest.tool.webrun.core.globalContext import g_context
                        g_context().set_dict(var_name, filepath)
                        print(f"[File] Download complete: {filepath}")
                        return
        raise TimeoutError(f"Download timeout: {download_dir}/{pattern}")

import time