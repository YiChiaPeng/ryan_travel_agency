import { Injectable, Inject, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable } from 'rxjs';
import { isPlatformBrowser } from '@angular/common';

export interface User {
  username: string;
  role: 'reviewer' | 'user'; // 審核者或一般使用者
  name: string;
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

  // 模擬用戶數據庫
  private users: User[] = [
    { username: 'reviewer1', role: 'reviewer', name: '張小明' },
    { username: 'reviewer2', role: 'reviewer', name: '李小華' },
    { username: 'user1', role: 'user', name: '王小美' },
    { username: 'user2', role: 'user', name: '陳小強' },
    { username: 'user3', role: 'user', name: '林小雅' }
  ];

  // 模擬審核記錄數據
  private reviewRecords: ReviewRecord[] = [
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
    },
    {
      id: 'R003',
      applicant: 'user3',
      applicantName: '林小雅',
      type: '文件修改',
      status: 'rejected',
      submitDate: '2025-09-18',
      description: '修改客戶資料文件',
      reviewer: 'reviewer2',
      reviewDate: '2025-09-18',
      reviewComment: '文件格式不符合要求'
    },
    {
      id: 'R004',
      applicant: 'user1',
      applicantName: '王小美',
      type: '權限申請',
      status: 'pending',
      submitDate: '2025-09-20',
      description: '申請管理員權限'
    },
    {
      id: 'R005',
      applicant: 'user2',
      applicantName: '陳小強',
      type: '文件上傳',
      status: 'approved',
      submitDate: '2025-09-17',
      description: '上傳行程安排文件',
      reviewer: 'reviewer1',
      reviewDate: '2025-09-17',
      reviewComment: '文件完整，通過審核'
    }
  ];

  constructor(
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);

    // 只在瀏覽器環境中檢查本地存儲
    if (this.isBrowser) {
      const isLoggedIn = localStorage.getItem('isLoggedIn');
      const username = localStorage.getItem('username');

      if (isLoggedIn === 'true' && username) {
        const user = this.users.find(u => u.username === username);
        if (user) {
          this.currentUserSubject.next(user);
        }
      }
    }
  }

  login(username: string, password: string): Observable<boolean> {
    return new Observable(observer => {
      // 模擬 API 調用 - 之後替換為真實的後端 API
      setTimeout(() => {
        // 簡單的密碼驗證邏輯（所有用戶密碼都是 '123456'）
        const user = this.users.find(u => u.username === username);
        if (user && password === '123456') {
          // 只在瀏覽器環境中儲存登入狀態
          if (this.isBrowser) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('username', username);
          }
          this.currentUserSubject.next(user);

          observer.next(true);
          observer.complete();
        } else {
          observer.next(false);
          observer.complete();
        }
      }, 1000); // 模擬網路延遲
    });
  }

  logout(): void {
    // 只在瀏覽器環境中清除登入狀態
    if (this.isBrowser) {
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('username');
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

  // 獲取審核記錄
  getReviewRecords(): ReviewRecord[] {
    const currentUser = this.currentUserSubject.value;
    if (!currentUser) return [];

    if (currentUser.role === 'reviewer') {
      // 審核者可以看到所有記錄
      return this.reviewRecords;
    } else {
      // 一般使用者只能看到自己的記錄
      return this.reviewRecords.filter(record => record.applicant === currentUser.username);
    }
  }

  // 獲取待審核記錄數量
  getPendingRecordsCount(): number {
    const currentUser = this.currentUserSubject.value;
    if (!currentUser) return 0;

    if (currentUser.role === 'reviewer') {
      return this.reviewRecords.filter(record => record.status === 'pending').length;
    } else {
      return this.reviewRecords.filter(record =>
        record.applicant === currentUser.username && record.status === 'pending'
      ).length;
    }
  }

  // 獲取已審核記錄數量
  getReviewedRecordsCount(): number {
    const currentUser = this.currentUserSubject.value;
    if (!currentUser) return 0;

    if (currentUser.role === 'reviewer') {
      return this.reviewRecords.filter(record => record.status !== 'pending').length;
    } else {
      return this.reviewRecords.filter(record =>
        record.applicant === currentUser.username && record.status !== 'pending'
      ).length;
    }
  }
}
