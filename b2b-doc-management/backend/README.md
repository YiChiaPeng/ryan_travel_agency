# Backend 說明（FastAPI）

本後端為基於 FastAPI 的服務，負責帳號與權限、申請案件與個人資料管理、檔案上傳，以及（可選）OCR/LLM 能力。採用分層設計：路由（Routers）→ 中介層/依賴（Middleware/Deps）→ 服務（Services）→ 資料庫（SQLAlchemy ORM）。

## 架構與主要元件

- `app/main.py`
	- 建立 `FastAPI` 應用、設定 CORS、在 `startup` 事件呼叫 `init_db()` 建表。
	- 掛載路由：
		- `app.routes`（舊版 `/api`）；
		- `app.routes_v2`（新版 `/api/v2`）；
		- `app.services.auth`（認證 `/auth`）。
		- `app.routes_ai`（AI 路由，預設註解停用）。

- 路由（Routers）
	- `app/routes.py`：舊版 API，提供上傳、記錄 CRUD、Excel 匯出等（`/api/...`）。
	- `app/routes_v2.py`：新版 API，聚焦「個人資料」「申請案件」的清楚模型與權限處理（`/api/v2/...`）。
	- `app/routes_ai.py`：OCR/LLM 端點（`/api/ocr/*`, `/api/llm/*`），預設停用可按需開啟。
	- `app/services/auth.py`：提供 `/auth/login|register|change-password|validate-token|refresh-token|logout`。

- 中介層/依賴（Middleware/Deps）
	- `app/middleware/auth.py`：
		- 解析 `Authorization: Bearer <token>`；
		- `get_current_user` 以 JWT 還原使用者；
		- `get_current_admin` 管理員驗證；
		- `verify_user_permission`、`verify_company_permission` 權限工具。

- 服務層（Services）
	- `app/services/auth_service.py`：登入/註冊/換密碼/驗證與刷新 JWT。
	- `app/services/individual_service.py`：個人資料 CRUD、Base64 圖片處理與擷取。
	- `app/services/application_service.py`：申請案件 CRUD、與個人資料的組合流程、分頁與管理員檢視。
	- `app/services/file_upload.py`：通用檔案上傳（預設寫入 `/tmp/uploads`）。
	- `app/services/notification.py`：用 SMTP 發信（以 `utils/smtp.py`）。
	- `app/services/ocr_service.py`：Tesseract OCR。
	- `app/services/llm_service.py`：OpenAI LLM 護照資訊解析。

- 公用工具（Utils）
	- `app/utils/db.py`：
		- 讀取 `DATABASE_URL` 建立 SQLAlchemy `engine`/`SessionLocal`/`Base`；
		- 啟動時 `wait_for_db()` 主動重試連線；
		- `init_db()` 由 `startup` 建表。
	- `app/utils/smtp.py`：SMTP 發送簡訊與設定載入。

- 資料模型（Models）`app/models.py`
	- `User`：使用者（含角色 `user/reviewer/admin/sudo` 與 `is_admin` 性質）。
	- `Individual`：個人資料（中文/英文姓名、身分證、性別、證件影像）。
	- `Application`：申請案件（類型/急件/狀態/理由等，關聯到 `User` 與 `Individual`）。
	- `Notification`：系統通知（對應 `User`）。
	- 舊模型：`Document`、`Upload`（為相容舊版 API 保留）。

## 請求處理流程（簡述）

```
Client → Router (/api 或 /api/v2) → 依賴注入 get_current_user → Service → ORM/DB → 回應
```

新版 `/api/v2` 端點將資料結構、錯誤處理與權限切分更清楚，建議新功能優先放在 V2。

## 認證與授權

- 認證：
	- `/auth/login` 成功後回傳 JWT，前端以 `Authorization: Bearer <token>` 傳遞。
	- `AuthService` 以固定常數 `SECRET_KEY` 產生/驗證 JWT（建議改用環境變數）。
	- Token 預設有效期 8 小時。
- 授權：
	- 以 `get_current_user` 取得目前登入者；
	- 透過 `is_admin`、`verify_user_permission`、`verify_company_permission` 控制權限；
	- 管理員端點會額外驗證 `current_user.is_admin`。

## 主要端點（節選）

- 舊版 `/api`
	- `POST /api/upload`：檔案上傳。
	- `GET /api/records`、`POST /api/records`：記錄查詢/新增（舊資料結構，對應 `Document`）。
	- `DELETE /api/record/{id}`、`POST /api/record/{id}/resubmit`。
	- `GET /api/export/{company}`：匯出 Excel。

- 新版 `/api/v2`
	- 個人資料：`POST /individuals`、`GET /individuals/{id}`、`PUT /individuals/{id}`、`GET /individuals/{id}/images/{front|back}`。
	- 申請案件：`POST /applications`、`GET /applications`、`GET /applications/{id}`、`PUT /applications/{id}`、`DELETE /applications/{id}`。
	- 管理員：`GET /admin/applications`（分頁）、`PUT /admin/applications/{id}/status`。

- 認證 `/auth`
	- `POST /auth/login|register|change-password|validate-token|refresh-token|logout`。

- AI（預設停用）`/api`
	- `POST /ocr/extract`、`GET /ocr/test`。
	- `POST /llm/extract-passport-info`、`GET /llm/test`、`POST /extract-passport-complete`。

## 設定與環境變數

- `DATABASE_URL`（必填）：如 `mariadb://backend:password@db:3306/b2b_doc`。
- SMTP：`SMTP_SERVER`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASSWORD`。
- `OPENAI_API_KEY`：啟用 LLM 功能必填。
- `JWT_SECRET_KEY`：目前未被 `AuthService` 使用；`AuthService` 內部用常數 `SECRET_KEY`，建議改為讀取此環境變數統一管理。

## 啟動與本地開發

安裝依賴與啟動（純 Python，本機）

```bash
pip install -r backend/requirements.txt
export DATABASE_URL="mariadb://backend:password@localhost:3307/b2b_doc"  # 依環境調整
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docker Compose（含 MariaDB、Mailhog、phpMyAdmin）

```bash
cd b2b-doc-management
docker-compose up -d
```

> 提醒：`utils/db.py` 在 import 時會執行 `wait_for_db()` 主動重試資料庫連線；可再搭配 Compose `healthcheck` 強化啟動順序。

## 資料與檔案處理

- 檔案上傳：`FileUploadService` 預設儲存於 `/tmp/uploads`，可依需求改路徑或接物件儲存。
- 影像欄位：`Individual` 支援以 Base64 上傳並存入 BLOB（護照資訊頁、身分證正反面）。
- 匯出：舊版 API 以 Pandas 產出 Excel（Streaming 回傳）。

## 故障排除

- 連 DB 失敗或 `Server has gone away`：
	- 確認 `db` 容器健康、`DATABASE_URL` 正確；
	- `utils/db.py` 已內建重試機制；
	- 可於 Compose 為 `db` 加上 `healthcheck`，讓 `backend` 以 `condition: service_healthy` 等待。
- OCR 失敗：
	- Dockerfile 已安裝 `tesseract-ocr` 與 `chi-tra/eng`，請確認容器內可執行；
	- 影像前處理在 `OCRService._preprocess_image` 可調整。
- LLM 不可用：
	- 確認 `OPENAI_API_KEY` 已設定；
	- 目前使用 `openai>=1.x` SDK，模型預設 `gpt-3.5-turbo`（可改）。

## 改進建議

- 將 `AuthService.SECRET_KEY` 改為讀取環境變數（與 `JWT_SECRET_KEY` 對齊）。
- 針對 `NotificationService` 檔案內重複定義進行清理（僅保留一次定義）。
- 為 `/api/v2` 增加更完整的回傳格式/錯誤碼統一化及 OpenAPI 標註。
- 將大型 BLOB 改為外部物件儲存（S3/minio），資料庫僅存連結與雜湊。

---

若需要，我可以：
- 加入 `db` 的 `healthcheck` 與 `backend` 等待條件；
- 將 `AuthService` 調整為讀取 `JWT_SECRET_KEY`；
- 產出 `/api/v2` 的端點清單與範例請求/回應 JSON。
