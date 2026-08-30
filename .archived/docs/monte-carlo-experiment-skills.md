# Skill Design: Probability Picker & Safety Control

## 通用「後續代理技能預測」技能設計概覽  

| 項目 | 說明 |
| ------ | ------ |
| **名稱** | `NextSkillPredictor`（後續技能預測器） |
| **觸發時機** | 代理工作流程 **內容生成完畢**、產出結果已生成 **且尚未交還給人類決策** 時自動啟動。 |
| **核心功能** | 1. 依據已完成的代理技能序列、上下文資訊與歷史執行資料，計算每個候選技能在當前情境下被選取的機率。<br>2. 取機率最高的 **前 5 名**，輸出：<br>   - 技能名稱（英文）<br>   - 機率（%）<br>   - 選取理由（繁體中文） |
| **輸出格式** | **雙輸出模式**：API 回傳 JSON Payload，前端 UI 渲染 Markdown 顯示表格。 |
| **使用的資料來源** | - **當前工作流狀態**：已執行的技能清單、輸入/輸出資料、錯誤訊息等。<br>- **全局知識庫**：所有已註冊的代理技能的功能描述、前置條件、後置條件。<br>- **歷史執行記錄**：相似情境下的實際選擇與成功率。 |
| **機率模型 (Batched Monte Carlo)** | 1. **特徵抽取 & 消毒 (Fix SEC-1)**：<br>   - 上下文文字包覆於 `<context_payload>` 標籤，剝離 Prompt 分隔符。<br>2. **批次模擬 (Fix S-2)**：<br>   - 6 批次 $\times$ 5 並列 Workers (共 $N=30$)，防範 API 429 Throttle。<br>3. **後處理 & 門檻**：<br>   - 依經驗機率排序，排除 $P < 10\%$ 項目。<br>   - **連鎖熔斷 (Fix S-1)**：重試次數 $\ge 3$ 強制 $P(\emptyset) = 1.0$。 |
| **安全與控制** | - **白名單驗證**：產出前強制比對授權技能白名單。<br>- **人類審核**：技能僅提供建議，最終決策仍由人類完成。<br>- **審計日誌**：每次預測的輸入、模型輸出與最終人類決策均寫入審計日誌。 |

---

## 預估問題與防範措施

| 類別 | 重點 | 說明 |
| ------ | ------ | ------ |
| **安全 (SEC-1)** | **Prompt Injection 消毒** | Raw 文本輸入前進行正則化過濾，強制包覆 XML 標籤並執行白名單過濾。 |
| **安定性 (S-1)** | **無限 Rewind 熔斷** | 設定 `MAX_CONSECUTIVE_REWINDS = 3` 硬上限，超過直接轉為 $\emptyset$ (Pass)。 |
| **效能 (S-2)** | **批次與 Rate-limit 防禦** | 設定 `BATCH_SIZE = 5` (6 批次)，Worker 間加 200ms 緩衝。 |
| **維護性 (N-1)** | **Schema 一致化** | 統一 JSON API 與 Markdown UI 表格欄位命名。 |
| **超參數 (N-2)** | **配置物件化** | 使用 `ProbabilityPickerConfig` 封裝 $N=30, \text{Temp}=0.3, \text{Threshold}=0.10$。 |

---

## 修正後 Verdict

**NEW VERDICT: `CLEAN`** (All criticals, warnings, and notes resolved across files).
