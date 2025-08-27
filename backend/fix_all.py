import os
import re

def fix_pydantic_issues(directory):
    """Arregla todos los problemas de compatibilidad de Pydantic"""
    fixed_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Cambiar regex= por pattern=
                    content = re.sub(r'\bregex=', 'pattern=', content)
                    
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Fixed: {filepath}")
                        fixed_files += 1
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    print(f"Fixed {fixed_files} files")

if __name__ == "__main__":
    fix_pydantic_issues("app")