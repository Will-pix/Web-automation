import os

path = 'core/resp_model.py'
try:
    with open(path, 'r', encoding='gbk') as f:
        content = f.read()
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {path}")
except Exception as e:
    print(f"Error: {e}")
    # Try reading as utf-8 just to see
    try:
        with open(path, 'r', encoding='utf-8') as f:
            print(f.read()[:100])
    except Exception as e2:
        print(f"Also failed utf-8: {e2}")
