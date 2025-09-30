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
  private readonly baseUrl = environment.apiUrl || 'http://localhost:5050';

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
}