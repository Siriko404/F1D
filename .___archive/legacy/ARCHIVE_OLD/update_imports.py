"""Update scripts to use step1_utils"""
import re
from pathlib import Path

scripts = [
    '2_Scripts/1_Sample/1.2_LinkEntities.py',
    '2_Scripts/1_Sample/1.3_BuildTenureMap.py', 
    '2_Scripts/1_Sample/1.4_AssembleManifest.py'
]

for script_path in scripts:
    p = Path(script_path)
    if p.exists():
        content = p.read_text(encoding='utf-8')
        
        # Add import
        if 'from step1_utils import' not in content:
            content = content.replace(
                'import shutil',
                'import shutil\nfrom step1_utils import generate_variable_reference, update_latest_symlink'
            )
        
        p.write_text(content, encoding='utf-8')
        print(f'Updated import: {script_path}')
