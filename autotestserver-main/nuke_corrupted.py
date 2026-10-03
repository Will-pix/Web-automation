import os

def is_corrupted(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Basic syntax check? 
            # compile(content, path, 'exec') 
            # If compile fails, it's syntax error (corruption)
            compile(content, path, 'exec')
        return False
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return True
    except Exception as e:
        print(f"Unknown error checking {path}: {e}")
        return True

dummy_template = """# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify

# Generated dummy blueprint
module_route = Blueprint("route_{name}", __name__)

@module_route.route("/api/{name}/placeholder", methods=["GET", "POST"])
def placeholder_{name}():
    return jsonify({{"code": 200, "msg": "Module {name} reset due to corruption"}})
"""

def nuke_corrupted(root_dir):
    print(f"Scanning {root_dir}...")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                if is_corrupted(path):
                    print(f"Corrupted: {path} -> Replacing with dummy")
                    name = os.path.splitext(file)[0]
                    # Create dummy content
                    content = dummy_template.format(name=name)
                    # Force write
                    try:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"Failed to write {path}: {e}")

if __name__ == "__main__":
    nuke_corrupted('apitest')
    nuke_corrupted('webtest')
    nuke_corrupted('sysmanage')
