import json

header = """# mattpocock skills lists

## 技能清單

/galab/yaochu/atmos/mattpocock-skills/skills/misc/scaffold-exercises/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/misc/migrate-to-shoehorn/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/misc/git-guardrails-claude-code/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/misc/setup-pre-commit/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/personal/edit-article/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/personal/obsidian-vault/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/to-questionnaire/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/setup-ts-deep-modules/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/writing-shape/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/writing-beats/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/writing-fragments/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/wizard/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/loop-me/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/batch-grill-me/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/in-progress/claude-handoff/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/deprecated/qa/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/deprecated/request-refactor-plan/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/deprecated/design-an-interface/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/deprecated/ubiquitous-language/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/codebase-design/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/research/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/wayfinder/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/to-spec/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/triage/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/to-tickets/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/improve-codebase-architecture/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/resolving-merge-conflicts/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/domain-modeling/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/tdd/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/grill-with-docs/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/code-review/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/implement/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/prototype/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/setup-matt-pocock-skills/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/ask-matt/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/engineering/diagnosing-bugs/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/productivity/grilling/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/productivity/grill-me/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/productivity/teach/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/productivity/writing-great-skills/SKILL.md
/galab/yaochu/atmos/mattpocock-skills/skills/productivity/handoff/SKILL.md

---

## Skills Lists 結構化 JSON 資料庫 (41 項完整清單)

包含 `engineering` (17項), `productivity` (5項), `personal` (2項), `misc` (4項), `in-progress` (9項), `deprecated` (4項) 之完整技能解析。

```json
"""

data = json.load(open('.scratch/mattpocock_skills_full.json'))
json_str = json.dumps(data, ensure_ascii=False, indent=2)

footer = """
```
"""

with open('docs/mattpocock-monte-carlo.md', 'w', encoding='utf-8') as f:
    f.write(header + json_str + footer)

print('Updated docs/mattpocock-monte-carlo.md successfully! Total skills:', len(data))
