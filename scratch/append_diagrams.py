# mattpocock skills lists

## 技能清單

"""
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
"""

## 開發生命週期狀態機流程圖 (Development Lifecycle State Machine)


```mermaid
stateDiagram-v2
    [*] --> Setup: 初始化與環境配置

    state Setup {
        [*] --> SetupSkills
        SetupSkills: setup-matt-pocock-skills / setup-pre-commit
        Guardrails: git-guardrails-claude-code
        SetupSkills --> Guardrails
    }

    Setup --> Triage: 環境準備完成

    state Triage {
        [*] --> IssueTriage
        IssueTriage: triage / to-tickets
        ResearchContext: research / wayfinder / ask-matt
        IssueTriage --> ResearchContext
    }

    Triage --> Architecture: 需求與問題梳理完畢

    state Architecture {
        [*] --> DesignSpec
        DesignSpec: codebase-design / domain-modeling / to-spec
        RefineArch: improve-codebase-architecture
        GrillDoc: grill-with-docs / grill-me / grilling
        DesignSpec --> RefineArch
        RefineArch --> GrillDoc
    }

    Architecture --> Prototyping: 規格與設計鎖定
    Architecture --> Implementation: 高確定性直接實作

    state Prototyping {
        [*] --> ProtoWork
        ProtoWork: prototype / wizard / writing-shape
        ProtoWork --> EvaluateProto
    }

    Prototyping --> Architecture: 原型驗證失敗 (重寫規格)
    Prototyping --> Implementation: 原型驗證成功 (開始開發)

    state Implementation {
        [*] --> CodeWork
        CodeWork: implement / tdd / setup-ts-deep-modules
        CodeWork --> VerifyCode
    }

    Implementation --> Debugging: 測試失敗 / 發現 Bug
    Implementation --> CodeReview: 實作完成

    state Debugging {
        [*] --> Diagnose
        Diagnose: diagnosing-bugs / resolving-merge-conflicts
        RefactorFix: migrate-to-shoehorn
        Diagnose --> RefactorFix
    }

    Debugging --> Implementation: 錯誤已修正 (回到開發)
    Debugging --> Architecture: 發現重大架構缺陷 (回頭重做)

    state CodeReview {
        [*] --> ReviewCode
        ReviewCode: code-review / batch-grill-me / loop-me
        ReviewCode --> AuditResult
    }

    CodeReview --> Debugging: 發現邏輯漏洞 / 測試未過
    CodeReview --> Handoff: 審查通過

    state Handoff {
        [*] --> DocumentHandoff
        DocumentHandoff: handoff / claude-handoff
        KnowledgeLoop: writing-great-skills / teach
        DocumentHandoff --> KnowledgeLoop
    }

    Handoff --> [*]: 任務交付完成
```

# ---

## 狀態機與動作類別對照關係 (State Machine & Action Taxonomy)

```mermaid
graph TD
    subgraph S1 ["1. 初始階段 (Setup State)"]
        S_Init["setup-matt-pocock-skills<br>setup-pre-commit"]
    end

    subgraph S2 ["2. 分流階段 (Triage State)"]
        S_Triage["triage<br>to-tickets<br>research<br>wayfinder"]
    end

    subgraph S3 ["3. 架構階段 (Architecture State)"]
        S_Arch["codebase-design<br>domain-modeling<br>to-spec<br>grill-with-docs"]
    end

    subgraph S4 ["4. 原型階段 (Prototyping State)"]
        S_Proto["prototype<br>wizard<br>writing-shape"]
    end

    subgraph S5 ["5. 實作階段 (Implementation State)"]
        S_Impl["implement<br>tdd<br>setup-ts-deep-modules"]
    end

    subgraph S6 ["6. 除錯階段 (Debugging State)"]
        S_Debug["diagnosing-bugs<br>resolving-merge-conflicts<br>migrate-to-shoehorn"]
    end

    subgraph S7 ["7. 審查階段 (Review State)"]
        S_Review["code-review<br>batch-grill-me<br>loop-me"]
    end

    subgraph S8 ["8. 交付階段 (Handoff State)"]
        S_Handoff["handoff<br>claude-handoff<br>writing-great-skills"]
    end

    %% 順向推進 (Forward Step)
    S_Init -->|Forward Step| S_Triage
    S_Triage -->|Forward Step| S_Arch
    S_Arch -->|Forward Step| S_Proto
    S_Proto -->|Forward Step| S_Impl
    S_Impl -->|Forward Step| S_Review
    S_Review -->|Forward Step| S_Handoff

    %% 本階段重試 (In-Phase Retry)
    S_Impl -->|In-Phase Retry| S_Debug
    S_Debug -->|In-Phase Retry| S_Impl

    %% 回頭重做 (Phase Rewind)
    S_Proto -.->|Phase Rewind| S_Arch
    S_Debug -.->|Phase Rewind| S_Arch
    S_Review -.->|Phase Rewind| S_Impl
    S_Review -.->|Phase Rewind| S_Arch

    %% 樣式設定
    style S1 fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff
    style S2 fill:#1f2937,stroke:#3b82f6,stroke-width:2px,color:#fff
    style S3 fill:#1f2937,stroke:#10b981,stroke-width:2px,color:#fff
    style S4 fill:#1f2937,stroke:#f59e0b,stroke-width:2px,color:#fff
    style S5 fill:#1f2937,stroke:#10b981,stroke-width:2px,color:#fff
    style S6 fill:#1f2937,stroke:#ef4444,stroke-width:2px,color:#fff
    style S7 fill:#1f2937,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style S8 fill:#1f2937,stroke:#06b6d4,stroke-width:2px,color:#fff
```
