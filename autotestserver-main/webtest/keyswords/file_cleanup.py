class file_cleanup:
    """Delete files matching pattern in a directory"""

    def __init__(self, driver):
        self.driver = driver

    def file_cleanup(self, **kwargs):
        import os
        import glob as glob_mod
        directory = kwargs.get("directory", "")
        pattern = kwargs.get("glob_pattern", "*")
        if not directory:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            from app import application
            directory = os.path.abspath(os.path.join(current_dir, application.config.get('UPLOAD_FOLDER', '../file')))
        elif not os.path.isabs(directory):
            directory = os.path.abspath(directory)
        if not os.path.exists(directory):
            print(f"[File] Directory not found, skipping: {directory}")
            return
        count = 0
        for f in glob_mod.glob(os.path.join(directory, pattern)):
            if os.path.isfile(f):
                os.remove(f)
                count += 1
        print(f"[File] Cleaned {count} files from {directory}")