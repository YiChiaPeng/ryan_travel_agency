# API Integration Examples

本文檔提供如何使用生成的 OpenAPI 規格與 API 整合的範例。

## 📦 使用 OpenAPI 規格

### 1. Postman Integration

#### 導入 OpenAPI 規格

1. 打開 Postman
2. 點擊 "Import"
3. 選擇 "Upload Files"
4. 選擇 `openapi.json` 文件
5. Postman 將自動創建所有 API 端點的集合

#### 配置環境變數

在 Postman 中設置環境變數：

```json
{
  "baseUrl": "http://localhost:8000",
  "token": "your-jwt-token-here"
}
```

### 2. 生成 TypeScript/JavaScript Client

使用 OpenAPI Generator 生成 TypeScript 客戶端：

```bash
# 安裝 OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# 生成 TypeScript Axios 客戶端
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o ./generated/typescript-client

# 生成 TypeScript Angular 客戶端
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-angular \
  -o ./generated/angular-client
```

#### 使用生成的客戶端

```typescript
import { Configuration, DefaultApi } from './generated/typescript-client';

// 配置 API 客戶端
const config = new Configuration({
  basePath: 'http://localhost:8000',
  accessToken: 'your-jwt-token'
});

const api = new DefaultApi(config);

// 使用 API
async function createIndividual() {
  try {
    const response = await api.createIndividualApiIndividualsPost({
      chinese_last_name: '王',
      chinese_first_name: '小明',
      english_last_name: 'Wang',
      english_first_name: 'XiaoMing'
    });
    console.log('個人資料已創建:', response.data);
  } catch (error) {
    console.error('錯誤:', error);
  }
}
```

### 3. Python Client 生成

```bash
# 生成 Python 客戶端
openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o ./generated/python-client
```

#### 使用 Python 客戶端

```python
from generated.python_client import ApiClient, Configuration, DefaultApi

# 配置
config = Configuration(
    host="http://localhost:8000",
    access_token="your-jwt-token"
)

# 創建客戶端
with ApiClient(config) as api_client:
    api = DefaultApi(api_client)
    
    # 調用 API
    response = api.create_individual_api_individuals_post(
        individual_request={
            "chinese_last_name": "王",
            "chinese_first_name": "小明",
            "english_last_name": "Wang",
            "english_first_name": "XiaoMing"
        }
    )
    print(f"個人資料已創建: {response}")
```

### 4. Swagger UI 本地運行

如果你想在不運行整個應用的情況下查看 API 文檔：

```bash
# 使用 Docker 運行 Swagger UI
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/openapi.json \
  -v $(pwd)/openapi.json:/openapi.json \
  swaggerapi/swagger-ui

# 訪問 http://localhost:8080
```

### 5. Mock Server with Prism

使用 Prism 創建基於規格的 Mock Server：

```bash
# 安裝 Prism
npm install -g @stoplight/prism-cli

# 啟動 Mock Server
prism mock openapi.json

# Mock Server 運行在 http://localhost:4010
```

#### 測試 Mock Server

```bash
# 測試端點
curl http://localhost:4010/api/individuals

# 查看可用端點
curl http://localhost:4010
```

### 6. 自動化測試

#### 使用 Dredd 進行契約測試

```bash
# 安裝 Dredd
npm install -g dredd

# 運行契約測試
dredd openapi.json http://localhost:8000
```

#### 使用 Schemathesis 測試

```bash
# 安裝 Schemathesis
pip install schemathesis

# 運行自動化測試
schemathesis run openapi.json --base-url http://localhost:8000
```

## 🔧 前端整合範例

### Angular Service 範例

基於 OpenAPI 規格手動創建的 Angular 服務：

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface IndividualRequest {
  chinese_last_name: string;
  chinese_first_name: string;
  english_last_name: string;
  english_first_name: string;
  id_card_front_image?: string;
  id_card_back_image?: string;
}

interface ApplicationRequest {
  application_type: string;
  urgency: string;
  application_date?: string;
  customer_name: string;
  status?: string;
  individual_data: IndividualRequest;
}

@Injectable({ providedIn: 'root' })
export class ApplicationService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000/api';

  createApplication(data: ApplicationRequest): Observable<any> {
    return this.http.post(`${this.baseUrl}/applications`, data);
  }

  getApplications(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/applications`);
  }

  getApplication(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/applications/${id}`);
  }

  updateApplication(id: number, data: Partial<ApplicationRequest>): Observable<any> {
    return this.http.put(`${this.baseUrl}/applications/${id}`, data);
  }

  deleteApplication(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/applications/${id}`);
  }
}
```

### React Hook 範例

```typescript
import { useState, useEffect } from 'react';

interface Application {
  id: number;
  application_type: string;
  urgency: string;
  customer_name: string;
  status: string;
}

export function useApplications() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/applications')
      .then(res => res.json())
      .then(data => {
        setApplications(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, []);

  return { applications, loading, error };
}
```

## 📊 API 監控和分析

### 使用 Swagger Stats

```bash
npm install swagger-stats
```

```javascript
const swStats = require('swagger-stats');
const apiSpec = require('./openapi.json');

app.use(swStats.getMiddleware({ 
  swaggerSpec: apiSpec,
  name: 'Ryan Travel Agency API',
  version: '1.0.0'
}));

// 訪問 http://localhost:8000/swagger-stats/ui
```

## 🔐 認證範例

### 使用 JWT Token

```typescript
// Angular Interceptor
import { Injectable, inject } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler } from '@angular/common/http';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    const token = localStorage.getItem('auth_token');
    
    if (token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      return next.handle(cloned);
    }
    
    return next.handle(req);
  }
}
```

### Fetch with Auth

```javascript
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('auth_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  });
  
  return response.json();
}

// 使用
const applications = await fetchWithAuth('http://localhost:8000/api/applications');
```

## 📝 額外資源

- [OpenAPI Generator 文檔](https://openapi-generator.tech/docs/generators)
- [Prism Mock Server](https://stoplight.io/open-source/prism)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Dredd API Testing](https://dredd.org/)
- [Schemathesis](https://schemathesis.readthedocs.io/)

---

有其他整合需求？請參考 [Spec-Driven Development Guide](../SPEC_DRIVEN_DEVELOPMENT.md)
