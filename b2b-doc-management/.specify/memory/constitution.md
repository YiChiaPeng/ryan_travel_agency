# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

# 專案憲章（Constitution）

## 1. 目標與願景
- 本專案致力於打造一個高可維護、易於協作、對人類友善的 B2B 文件管理平台。
- 前端採用 Angular，後端採用 FastAPI，所有服務以 Docker Compose 管理，確保部署與開發一致性。

## 2. 設計原則
- **規格優先（Spec-Driven）**：所有 API、資料結構、流程變更，皆以規格文件（OpenAPI/JSON Schema）為單一事實來源，先審規格、後實作。
- **可讀性優先**：程式碼、文件、規格皆以清晰、簡潔、中文註解為主，降低新進人員理解門檻。
- **模組化與分層**：前後端、各微服務、資料庫、CI/CD 流程皆明確分層，責任單一，易於替換與擴展。
- **自動化**：測試、建置、部署、規格驗證皆自動化，減少人為疏失。

## 3. 協作規範
- **分支策略**：所有功能、修正、規格變更皆以 Pull Request 進行，需通過自動化檢查與 CODEOWNERS 審核。
- **規格審查**：API/資料結構變更，需先提交規格 PR，通過後方可進行實作 PR。
- **文件同步**：每次功能/規格變更，需同步更新對應文件（README、OpenAPI、JSON Schema、前端型別）。
- **中文優先**：所有對外文件、註解、介面皆以中文為主，必要時附英文備註。

## 4. 維護與可持續性
- **版本管理**：嚴格遵循語意化版本（SemVer），破壞性變更需公告並提供遷移指引。
- **汰舊策略**：舊 API/功能將標註 deprecated，並於 changelog 記錄 sunset 時程。
- **測試覆蓋**：所有服務需具備單元測試、整合測試，並於 CI 強制執行。

## 5. 人本導向
- **易學易用**：新進開發者可依文件快速上手，遇到問題可於專案 Q&A 或文件中查詢。
- **開放討論**：鼓勵團隊成員提出改進建議，定期檢討與優化專案流程與技術選型。
## Core Principles


### I. 代碼品質與可讀性（Code Quality & Readability）
所有程式碼必須遵循團隊風格指南，保持一致命名、結構與註解。嚴禁未經審查的 quick fix、magic number、複雜巢狀。每次 PR 需經過自動化靜態分析（如 lint、format）與人工審查。

### II. 測試標準（Testing Standards）
所有功能必須具備單元測試與整合測試，覆蓋主要邏輯與邊界情境。CI pipeline 必須強制通過測試，破壞性變更需有回歸測試。測試案例需易讀、可重現，並與規格同步。

### III. 使用者體驗一致性（User Experience Consistency）
前端 UI/UX 必須遵循設計規範，確保元件、流程、用詞、錯誤訊息一致。多語系介面需同步維護。所有互動需有明確回饋，避免用戶困惑。

### IV. 效能要求（Performance Requirements）
後端 API 必須在預期負載下於 200ms 內回應（95 百分位），前端頁面載入時間須小於 2 秒。所有效能瓶頸需有監控與警示，重大效能優化需記錄於 changelog。

### V. 文件與可維護性（Documentation & Maintainability）
所有公開 API、資料結構、複雜邏輯必須有完整文件。文件需與實作同步，並以中文為主。程式碼 refactor、重構需有明確 commit 訊息與說明。

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->


## 附加約束與安全性（Additional Constraints & Security）
- 僅允許經審查的第三方套件，並定期檢查漏洞。
- 敏感資訊（如密碼、金鑰）不得寫死於程式碼，必須用環境變數或安全儲存。
- 所有 API 需有權限驗證與存取控制。


## 開發流程與品質門檻（Development Workflow & Quality Gates）
- 所有開發需以 issue/規格為依據，禁止無 ticket 直接開發。
- PR 必須通過自動化檢查（lint、test、build）與至少一位 reviewer 審查。
- 重大變更需有設計審查會議紀錄。
- 部署前必須通過 staging 測試與驗收。


## 治理機制（Governance）
- 本憲章優先於其他開發慣例，所有團隊成員必須遵守。
- 憲章修訂需經團隊共識，並記錄修訂日期與版本。
- 重大違規需提出說明與改善計畫。
- 所有 PR/Review 必須檢查是否符合本憲章原則。

**Version**: 1.0.0 | **Ratified**: 2025-11-17 | **Last Amended**: 2025-11-17

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
