import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApplicationService, Application, ApplicationStatus } from '../application';
import { Auth } from '../auth';

@Component({
  selector: 'app-application-history',
  imports: [CommonModule, FormsModule],
  templateUrl: './application-history.html',
  styleUrl: './application-history.css'
})
export class ApplicationHistory implements OnInit {
  private applicationService = inject(ApplicationService);
  private auth = inject(Auth);
  private router = inject(Router);

  applications: Application[] = [];
  filteredApplications: Application[] = [];
  selectedStatus: ApplicationStatus | 'all' = 'all';
  searchTerm = '';

  // 狀態篩選選項
  statusOptions: { value: ApplicationStatus | 'all', label: string, color: string }[] = [
    { value: 'all', label: '全部', color: '#718096' },
    { value: 'draft', label: '草稿', color: '#a0aec0' },
    { value: 'submitted', label: '已提交', color: '#3182ce' },
    { value: 'under_review', label: '審核中', color: '#d69e2e' },
    { value: 'approved', label: '已通過', color: '#38a169' },
    { value: 'rejected', label: '已拒絕', color: '#e53e3e' },
    { value: 'completed', label: '已完成', color: '#38a169' }
  ];

  ngOnInit() {
    this.loadApplications();
  }

  private loadApplications() {
    const currentUser = this.auth.getCurrentUser();
    if (currentUser) {
      this.applications = this.applicationService.getUserApplications(currentUser.username);
      this.filterApplications();
    }
  }

  filterApplications() {
    let filtered = this.applications;

    // 狀態篩選
    if (this.selectedStatus !== 'all') {
      filtered = filtered.filter(app => app.status === this.selectedStatus);
    }

    // 搜尋篩選
    if (this.searchTerm.trim()) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(app =>
        app.customerName.toLowerCase().includes(term) ||
        app.type.toLowerCase().includes(term) ||
        app.id.toLowerCase().includes(term)
      );
    }

    this.filteredApplications = filtered.sort((a, b) =>
      new Date(b.applicationDate).getTime() - new Date(a.applicationDate).getTime()
    );
  }

  onStatusChange() {
    this.filterApplications();
  }

  onSearchChange() {
    this.filterApplications();
  }

  getStatusLabel(status: ApplicationStatus): string {
    const statusMap: { [key in ApplicationStatus]: string } = {
      draft: '草稿',
      submitted: '已提交',
      under_review: '審核中',
      approved: '已通過',
      rejected: '已拒絕',
      completed: '已完成'
    };
    return statusMap[status];
  }

  getStatusColor(status: ApplicationStatus): string {
    const colorMap: { [key in ApplicationStatus]: string } = {
      draft: '#a0aec0',
      submitted: '#3182ce',
      under_review: '#d69e2e',
      approved: '#38a169',
      rejected: '#e53e3e',
      completed: '#38a169'
    };
    return colorMap[status];
  }

  getStatusIcon(status: ApplicationStatus): string {
    const iconMap: { [key in ApplicationStatus]: string } = {
      draft: '📝',
      submitted: '📤',
      under_review: '⏳',
      approved: '✅',
      rejected: '❌',
      completed: '🎉'
    };
    return iconMap[status];
  }

  editApplication(application: Application) {
    this.router.navigate(['/application-form'], {
      state: { application }
    });
  }

  createNewApplication() {
    this.router.navigate(['/application-form']);
  }

  deleteApplication(application: Application) {
    if (confirm(`確定要刪除申請 "${application.customerName}" 嗎？`)) {
      this.applicationService.deleteApplication(application.id).subscribe({
        next: (success) => {
          if (success) {
            this.loadApplications();
          }
        },
        error: (error) => {
          console.error('Delete application error:', error);
        }
      });
    }
  }

  canEditApplication(application: Application): boolean {
    return application.status === 'draft' || application.status === 'rejected';
  }

  canDeleteApplication(application: Application): boolean {
    return application.status === 'draft';
  }

  getApplicationProgress(application: Application): number {
    const statusProgress: { [key in ApplicationStatus]: number } = {
      draft: 10,
      submitted: 30,
      under_review: 60,
      approved: 80,
      rejected: 100,
      completed: 100
    };
    return statusProgress[application.status];
  }

  // 統計數據
  get pendingCount(): number {
    return this.applications.filter(a => a.status === 'submitted' || a.status === 'under_review').length;
  }

  get approvedCount(): number {
    return this.applications.filter(a => a.status === 'approved' || a.status === 'completed').length;
  }

  get rejectedCount(): number {
    return this.applications.filter(a => a.status === 'rejected').length;
  }
}
