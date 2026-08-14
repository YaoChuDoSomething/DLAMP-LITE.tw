import os
import re
import json
from pathlib import Path
from datetime import datetime

def parse_frontmatter(content):
    """Extracts YAML-like frontmatter from the top of a markdown file."""
    match = re.match(r'^---\s*([\s\S]*?)\s*---\s*([\s\S]*)$', content)
    if not match:
        return None, content
    
    fm_raw = match.group(1)
    body = match.group(2)
    
    fm = {}
    for line in fm_raw.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip().strip('"').strip("'")
            
    return fm, body

def extract_analysis(body):
    """Extracts behavioral constraints and process steps from the body."""
    lines = body.split('\n')
    precondition = []
    postcondition = []
    best_practice = []
    dont = []
    
    for line in lines:
        l = line.strip()
        low = l.lower()
        
        # Preconditions
        if low.startswith('use when') or 'precondition' in low:
            precondition.append(l)
        # Postconditions
        elif low.startswith('report') or 'outcome' in low or 'end with' in low:
            postcondition.append(l)
        # Best Practices
        elif low.startswith('do ') or 'should' in low:
            best_practice.append(l)
        # Prohibitions
        elif low.startswith('do not') or "don't" in low or 'skip' in low:
            dont.append(l)
            
    return {
        "precondition": precondition[:5],
        "postcondition": postcondition[:5],
        "best_practice": best_practice[:5],
        "don_t": dont[:5]
    }

def process_skills(base_dir, output_file):
    skills_index = {}
    base_path = Path(base_dir)
    
    # Find all SKILL.md files recursively
    skill_files = list(base_path.rglob('SKILL.md'))
    
    for skill_file in skill_files:
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fm, body = parse_frontmatter(content)
            if fm is None:
                continue
                
            skill_name = fm.get('name') or skill_file.parent.name
            category = skill_file.parent.parent.name if skill_file.parent.parent != base_path else 'misc'
            
            analysis = extract_analysis(body)
            
            # Map status based on category
            status = 'active'
            if category == 'deprecated':
                status = 'deprecated'
            elif category == 'in-progress':
                status = 'in-progress'
                
            skills_index[skill_name] = {
                "markdown_source": str(skill_file),
                "category": category,
                "tags": [], # To be filled manually or via keyword extraction
                "status": status,
                "last_touched": datetime.now().isoformat(),
                "brief_english": fm.get('description', ''),
                "brief_traditional": "", # Manual translation
                "precondition": analysis['precondition'],
                "postcondition": analysis['postcondition'],
                "best_practice": analysis['best_practice'],
                "don_t": analysis['don_t'],
                "error_handling": [],
                "testing": []
            }
        except Exception as e:
            print(f"Error processing {skill_file}: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(skills_index, f, indent=2, ensure_ascii=False)
        
    return len(skills_index)

if __name__ == "__main__":
    # Paths based on the provided environment
    INPUT_DIR = '/galab/yaochu/atmos/mattpocock-skills/skills'
    OUTPUT_PATH = '/wk2/yaochu/main/dlamp/.scratch/mattpocock_skills_full.json'
    
    count = process_skills(INPUT_DIR, OUTPUT_PATH)
    print(f"Successfully processed {count} skills into {OUTPUT_PATH}")
