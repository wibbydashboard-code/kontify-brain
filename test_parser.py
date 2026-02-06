
import os
import sys
import json
from flask import Flask, jsonify

# Agregar el directorio /tools al path
sys.path.append(os.path.join(os.getcwd(), 'tools'))

def test_parsing():
    from server import get_questions
    
    files = [
        'holding_grupo_diagnostico.md',
        'constructora_diagnostico.md',
        'manufactura_transformacion_diagnostico.md'
    ]
    
    for f in files:
        print(f"\n--- Testing {f} ---")
        # Mocking the call that server.py would make
        # We need to simulate the file existing in the right place
        questions = []
        import re
        current_category = "General"
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                cat_match = re.search(r'##\s+\w+\.\s+([^(]+)', line)
                if cat_match:
                    current_category = cat_match.group(1).strip()
                    continue
                q_match = re.search(r'^(\d+)\.\s+(.+)$', line)
                if q_match:
                    full_text = q_match.group(2).strip()
                    options = []
                    opt_match = re.search(r'\[([^\]]+)\]$', full_text)
                    if opt_match:
                        options_raw = opt_match.group(1)
                        options = [o.strip() for o in options_raw.split('|')]
                        full_text = full_text.replace(opt_match.group(0), '').strip()
                    
                    if options:
                        print(f"Q: {full_text} -> Options: {options}")
                    
if __name__ == "__main__":
    test_parsing()
