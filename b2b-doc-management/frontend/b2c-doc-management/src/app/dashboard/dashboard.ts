import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Auth, User, ReviewRecord } from '../auth';
import { ApplicationService, Application } from '../application';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  private auth = inject(Auth);
  private router = inject(Router);
  private applicationService = inject(ApplicationService);

  currentUser: User | null = null;
  reviewRecords: ReviewRecord[] = [];
  applications: Application[] = [];
  pendingCount: number = 0;
  reviewedCount: number = 0;
  totalApplications: number = 0;
  
  // 使用者選單狀態
  isUserMenuOpen = false;

  ngOnInit() {
    // 檢查登入狀態
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    this.currentUser = this.auth.getCurrentUser();
    this.loadData();
  }

  private loadData() {
    if (this.currentUser?.role === 'reviewer') {
      // 審核員：載入所有審核記錄
      this.auth.getReviewRecords().subscribe(records => {
        this.reviewRecords = records;
      });
      
      this.auth.getPendingRecordsCount().subscribe(count => {
        this.pendingCount = count;
      });
      
      this.auth.getReviewedRecordsCount().subscribe(count => {
        this.reviewedCount = count;
      });
    } else {
      // 普通用戶：載入自己的申請記錄
      this.applications = this.applicationService.getUserApplications(this.currentUser?.username || '');
      this.totalApplications = this.applications.length;
      this.pendingCount = this.applications.filter(app => app.status === 'submitted' || app.status === 'under_review').length;
      this.reviewedCount = this.applications.filter(app => app.status === 'approved' || app.status === 'completed' || app.status === 'rejected').length;
    }
  }

  logout() {
    this.auth.logout();
  }

  // 導航方法
  createNewApplication() {
    this.router.navigate(['/application-form']);
  }

  viewApplicationHistory() {
    this.router.navigate(['/application-history']);
  }

  // 審核員相關方法
  getStatusText(status: string): string {
    switch (status) {
      case 'pending': return '待審核';
      case 'approved': return '已通過';
      case 'rejected': return '已拒絕';
      default: return '未知';
    }
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'pending': return 'status-pending';
      case 'approved': return 'status-approved';
      case 'rejected': return 'status-rejected';
      default: return '';
    }
  }

  // 應用程序相關方法
  getApplicationStatusText(status: string): string {
    switch (status) {
      case 'draft': return '草稿';
      case 'submitted': return '已提交';
      case 'under_review': return '審核中';
      case 'approved': return '已通過';
      case 'rejected': return '已拒絕';
      case 'completed': return '已完成';
      default: return '未知';
    }
  }

  getApplicationStatusColor(status: string): string {
    switch (status) {
      case 'draft': return '#718096';
      case 'submitted': return '#3182ce';
      case 'under_review': return '#d69e2e';
      case 'approved': return '#38a169';
      case 'rejected': return '#e53e3e';
      case 'completed': return '#38a169';
      default: return '#718096';
    }
  }

  getRoleText(role: string): string {
    return role === 'reviewer' ? '審核者' : '一般使用者';
  }

  // 使用者選單控制
  toggleUserMenu() {
    this.isUserMenuOpen = !this.isUserMenuOpen;
  }

  // 導航到帳號設定
  navigateToAccountSettings() {
    this.isUserMenuOpen = false;
    this.router.navigate(['/account-settings']);
  }

  // 點擊外部關閉選單（可在 HTML 中使用）
  closeUserMenu() {
    this.isUserMenuOpen = false;
  }
}
