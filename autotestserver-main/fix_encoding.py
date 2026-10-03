import os

def convert_encoding(root_dir):
    print(f"Scanning {root_dir}...")
    for root, dirs, files in os.walk(root_dir):
        if 'venv' in dirs:
            # Skip venv
            continue
            
        # Also skip .git or __pycache__ if needed, but os.walk handles dirs
        # Manually filter dirs to avoid descending into venv
        dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__']]

        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    # Try reading as GBK (common Windows PowerShell output)
                    with open(path, 'r', encoding='gbk') as f:
                        content = f.read()
                    
                    # Write back as UTF-8
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Fixed: {path}")
                except UnicodeDecodeError:
                    # If it's not valid GBK, it might mean it's already UTF-8 or binary garbage
                    # Try reading as UTF-8 to confirm it's okay
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            f.read()
                        # print(f"OK (UTF-8): {path}")
                    except:
                        print(f"Warning: Could not decode {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    convert_encoding('.')
