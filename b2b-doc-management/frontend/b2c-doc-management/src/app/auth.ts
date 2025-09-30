import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { ApiService, LoginRequest, RegisterRequest } from './api.service';

export interface User {
  id: number;
  username: string;
  company: string;
  token: string;
  role: string;
  name: string;
  email?: string;
  is_admin: boolean;
}

export interface ReviewRecord {
  id: string;
  applicant: string;
  applicantName: string;
  type: string;
  status: 'pending' | 'approved' | 'rejected';
  submitDate: string;
  description: string;
  reviewer?: string;
  reviewDate?: string;
  reviewComment?: string;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  private isBrowser: boolean;

  constructor(
    private router: Router,
    private apiService: ApiService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);

    // 只在瀏覽器環境中檢查本地存儲
    if (this.isBrowser) {
      const userData = localStorage.getItem('currentUser');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          // 檢查 token 是否還有效（這裡可以加入 token 過期檢查）
          if (user.token && user.id && user.username) {
            this.currentUserSubject.next(user);
          }
        } catch (error) {
          console.error('Invalid user data in localStorage:', error);
          localStorage.removeItem('currentUser');
        }
      }
    }
  }

  login(username: string, password: string): Observable<boolean> {
    const loginRequest: LoginRequest = { username, password };
    
    return this.apiService.login(loginRequest).pipe(
      map(response => {
        if (response && response.user) {
          const user: User = {
            id: response.user.id,
            username: response.user.username,
            company: response.user.company || '',
            token: response.user.token,
            role: response.user.role,
            name: response.user.username,
            email: '',
            is_admin: response.user.is_admin
          };

          // 只在瀏覽器環境中儲存登入狀態
          if (this.isBrowser) {
            localStorage.setItem('currentUser', JSON.stringify(user));
          }
          
          this.currentUserSubject.next(user);
          return true;
        }
        return false;
      }),
      catchError(error => {
        console.error('Login error:', error);
        return of(false);
      })
    );
  }

  logout(): void {
    const currentUser = this.getCurrentUser();
    if (currentUser && currentUser.token) {
      // 呼叫backend的logout API
      this.apiService.logout(currentUser.token).subscribe({
        next: () => {
          console.log('Logout successful');
        },
        error: (error) => {
          console.error('Logout error:', error);
        }
      });
    }

    // 清除本地狀態
    if (this.isBrowser) {
      localStorage.removeItem('currentUser');
    }
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return this.currentUserSubject.value !== null;
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    const user = this.getCurrentUser();
    return user ? user.token : null;
  }

  // 註冊新用戶
  register(username: string, password: string, company?: string, email?: string): Observable<boolean> {
    const registerRequest: RegisterRequest = { username, password, company, email };
    return this.apiService.register(registerRequest).pipe(
      map(response => {
        if (response && response.user) {
          // 註冊成功後可以選擇自動登入或要求用戶手動登入
          return true;
        }
        return false;
      }),
      catchError(error => {
        console.error('Register error:', error);
        return of(false);
      })
    );
  }

  // 獲取審核記錄（暫時使用模擬數據，因為後端還沒有相應 API）
  getReviewRecords(): Observable<ReviewRecord[]> {
    // 模擬一些記錄數據
    const mockRecords: ReviewRecord[] = [
      {
        id: 'R001',
        applicant: 'user1',
        applicantName: '王小美',
        type: '文件上傳',
        status: 'pending',
        submitDate: '2025-09-20',
        description: '上傳旅行社合約文件'
      },
      {
        id: 'R002',
        applicant: 'user2',
        applicantName: '陳小強',
        type: '權限申請',
        status: 'approved',
        submitDate: '2025-09-19',
        description: '申請文檔編輯權限',
        reviewer: 'reviewer1',
        reviewDate: '2025-09-19',
        reviewComment: '已通過審核'
      }
    ];

    return of(mockRecords);
  }

  // 獲取待審核記錄數量
  getPendingRecordsCount(): Observable<number> {
    return this.getReviewRecords().pipe(
      map(records => records.filter(record => record.status === 'pending').length)
    );
  }

  // 獲取已審核記錄數量
  getReviewedRecordsCount(): Observable<number> {
    return this.getReviewRecords().pipe(
      map(records => records.filter(record => record.status !== 'pending').length)
    );
  }
}
