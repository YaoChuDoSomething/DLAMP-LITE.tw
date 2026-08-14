import json
import os
from pathlib import Path

def generate_prompt_content(skill_name, data):
    """Generates a high-quality prompt based on the skill's structured data."""
    brief = data.get('brief_english', '')
    pre = "\n".join([f"- {item}" for item in data.get('precondition', [])])
    post = "\n".join([f"- {item}" for item in data.get('postcondition', [])])
    bp = "\n".join([f"- {item}" for item in data.get('best_practice', [])])
    dt = "\n".join([f"- {item}" for item in data.get('don_t', [])])
    
    prompt = f'''# {skill_name.replace("-", " ").title()}

{brief}

## Operational Guidelines:

### Preconditions (When to act):
{pre if pre else "No specific preconditions defined."}

### Best Practices (How to succeed):
{bp if bp else "Follow general project standards."}

### Constraints (What to avoid):
{dt if dt else "No specific prohibitions defined."}

### Expected Outcome:
{post if post else "Complete the task as specified in the skill definition."}

## Execution:
1. Analyze the current context and verify preconditions.
2. Apply the best practices mentioned above.
3. Execute the skill logic strictly avoiding the listed constraints.
4. Provide the output in the expected format.

Input:
```
{{args}}
```
'''
    return f'prompt = """\\n{prompt}\\n"""'

def main():
    json_path = '/wk2/yaochu/main/dlamp/.scratch/mattpocock_skills_full.json'
    output_base = Path('/wk2/yaochu/main/dlamp/.agents/commands')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        skills = json.load(f)
    
    for name, data in skills.items():
        category = data.get('category', 'misc')
        # Create category directory
        cat_dir = output_base / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate TOML content
        toml_content = generate_prompt_content(name, data)
        
        # Write to .toml file
        file_path = cat_dir / f"{name}.toml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(toml_content)
            
    print(f"Successfully generated {len(skills)} prompt templates in {output_base}")

if __name__ == "__main__":
    main()
