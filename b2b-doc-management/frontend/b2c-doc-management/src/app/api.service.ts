import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  user: {
    id: number;
    username: string;
    company: string;
    role: string;
    is_admin: boolean;
    token: string;
  };
}

export interface RegisterRequest {
  username: string;
  password: string;
  company?: string;
  email?: string;
}

export interface RegisterResponse {
  message: string;
  user: {
    id: number;
    username: string;
    company: string;
    role: string;
    is_admin: boolean;
    token: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = environment.apiUrl || '';

  constructor(private http: HttpClient) {}

  // 登入
  login(request: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/auth/login`, request);
  }

  // 註冊
  register(request: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.baseUrl}/auth/register`, request);
  }

  // 登出
  logout(token: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/logout`, { token });
  }

  // 更改密碼
  changePassword(username: string, oldPassword: string, newPassword: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/change-password`, {
      username,
      old_password: oldPassword,
      new_password: newPassword
    });
  }

  // === Admin: Users CRUD ===
  private authHeaders(token: string): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  getUsers(token: string, page: number = 1, limit: number = 50): Observable<any> {
    const headers = this.authHeaders(token);
    return this.http.get(`${this.baseUrl}/api/admin/users`, { headers, params: { page, limit } as any });
  }

  getUser(token: string, userId: number): Observable<any> {
    const headers = this.authHeaders(token);
    return this.http.get(`${this.baseUrl}/api/admin/users/${userId}`, { headers });
  }

  createUser(token: string, payload: { username: string; password: string; company_name?: string; email?: string; role?: string; }): Observable<any> {
    const headers = this.authHeaders(token);
    return this.http.post(`${this.baseUrl}/api/admin/users`, payload, { headers });
  }

  updateUser(token: string, userId: number, payload: Partial<{ username: string; password: string; company_name: string; email: string; role: string; }>): Observable<any> {
    const headers = this.authHeaders(token);
    return this.http.put(`${this.baseUrl}/api/admin/users/${userId}`, payload, { headers });
  }

  deleteUser(token: string, userId: number): Observable<any> {
    const headers = this.authHeaders(token);
    return this.http.delete(`${this.baseUrl}/api/admin/users/${userId}`, { headers });
  }
}