import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

// 申請類型
export type ApplicationType = '首次申請' | '換證' | '遺失件';

// 辦理速度
export type ProcessingSpeed = '急件' | '普通件';

// 申請狀態
export type ApplicationStatus = 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'completed';

// 個人資料介面
export interface Individual {
  id?: number;
  chinese_last_name: string;
  chinese_first_name: string;
  english_last_name: string;
  english_first_name: string;
  national_id: string;
  birth_date: string;
  passport_infomation_image?: string;
  id_card_front_image?: string;
  id_card_back_image?: string;
  created_at?: string;
  updated_at?: string;
}

// 附件類型
export interface Attachment {
  id: string;
  name: string;
  type: '戶謄' | '父親身分證' | '母親身分證' | '聲明書' | '報案單' | '舊台胞卡' | '舊台胞證影本' | '其他';
  file: File;
  uploadDate: string;
  size: number;
}

// 申請資料模型
export interface Application {
  id: string;
  applicantId: string;
  applicantName: string;
  type: ApplicationType;
  speed: ProcessingSpeed;
  applicationDate: string;
  customerName: string;
  status: ApplicationStatus;
  attachments: Attachment[];
  individual?: Individual;  // 個人詳細資料
  submitDate?: string;
  reviewDate?: string;
  reviewerId?: string;
  reviewerName?: string;
  reviewComment?: string;
  notes?: string;
}

// 申請服務
@Injectable({
  providedIn: 'root'
})
export class ApplicationService {
  private applications: Application[] = [
    // 模擬數據
    {
      id: 'APP001',
      applicantId: 'user1',
      applicantName: '王小美',
      type: '首次申請',
      speed: '普通件',
      applicationDate: '2025-09-20',
      customerName: '張三',
      status: 'submitted',
      attachments: [],
      submitDate: '2025-09-20'
    },
    {
      id: 'APP002',
      applicantId: 'user2',
      applicantName: '陳小強',
      type: '換證',
      speed: '急件',
      applicationDate: '2025-09-19',
      customerName: '李四',
      status: 'under_review',
      attachments: [],
      submitDate: '2025-09-19'
    },
    {
      id: 'APP003',
      applicantId: 'user1',
      applicantName: '王小美',
      type: '遺失件',
      speed: '普通件',
      applicationDate: '2025-09-18',
      customerName: '王五',
      status: 'approved',
      attachments: [],
      submitDate: '2025-09-18',
      reviewDate: '2025-09-19',
      reviewerId: 'reviewer1',
      reviewerName: '張小明',
      reviewComment: '文件齊全，通過審核'
    }
  ];

  private applicationsSubject = new BehaviorSubject<Application[]>(this.applications);
  public applications$ = this.applicationsSubject.asObservable();

  constructor() {}

  // 獲取用戶的申請列表
  getUserApplications(userId: string): Application[] {
    return this.applications.filter(app => app.applicantId === userId);
  }

  // 獲取所有申請（審核者使用）
  getAllApplications(): Application[] {
    return this.applications;
  }

  // 根據狀態獲取申請
  getApplicationsByStatus(userId: string, status?: ApplicationStatus): Application[] {
    let apps = this.applications.filter(app => app.applicantId === userId);
    if (status) {
      apps = apps.filter(app => app.status === status);
    }
    return apps;
  }

  // 創建新申請
  createApplication(application: Omit<Application, 'id' | 'status'>): Observable<Application> {
    return new Observable(observer => {
      setTimeout(() => {
        const newApplication: Application = {
          ...application,
          id: 'APP' + (this.applications.length + 1).toString().padStart(3, '0'),
          status: 'draft'
        };

        this.applications.push(newApplication);
        this.applicationsSubject.next([...this.applications]);

        observer.next(newApplication);
        observer.complete();
      }, 500);
    });
  }

  // 更新申請
  updateApplication(id: string, updates: Partial<Application>): Observable<Application> {
    return new Observable(observer => {
      setTimeout(() => {
        const index = this.applications.findIndex(app => app.id === id);
        if (index !== -1) {
          this.applications[index] = { ...this.applications[index], ...updates };
          this.applicationsSubject.next([...this.applications]);
          observer.next(this.applications[index]);
        } else {
          observer.error('Application not found');
        }
        observer.complete();
      }, 500);
    });
  }

  // 提交申請
  submitApplication(id: string): Observable<Application> {
    return this.updateApplication(id, {
      status: 'submitted',
      submitDate: new Date().toISOString().split('T')[0]
    });
  }

  // 刪除申請（草稿狀態）
  deleteApplication(id: string): Observable<boolean> {
    return new Observable(observer => {
      setTimeout(() => {
        const index = this.applications.findIndex(app => app.id === id);
        if (index !== -1 && this.applications[index].status === 'draft') {
          this.applications.splice(index, 1);
          this.applicationsSubject.next([...this.applications]);
          observer.next(true);
        } else {
          observer.next(false);
        }
        observer.complete();
      }, 500);
    });
  }

  // 獲取申請詳情
  getApplicationById(id: string): Application | null {
    return this.applications.find(app => app.id === id) || null;
  }

  // 上傳附件
  uploadAttachment(applicationId: string, attachment: Omit<Attachment, 'id' | 'uploadDate'>): Observable<Attachment> {
    return new Observable(observer => {
      setTimeout(() => {
        const application = this.applications.find(app => app.id === applicationId);
        if (application) {
          const newAttachment: Attachment = {
            ...attachment,
            id: 'ATT' + Date.now(),
            uploadDate: new Date().toISOString()
          };

          application.attachments.push(newAttachment);
          this.applicationsSubject.next([...this.applications]);

          observer.next(newAttachment);
        } else {
          observer.error('Application not found');
        }
        observer.complete();
      }, 1000);
    });
  }

  // 刪除附件
  deleteAttachment(applicationId: string, attachmentId: string): Observable<boolean> {
    return new Observable(observer => {
      setTimeout(() => {
        const application = this.applications.find(app => app.id === applicationId);
        if (application) {
          const attachmentIndex = application.attachments.findIndex(att => att.id === attachmentId);
          if (attachmentIndex !== -1) {
            application.attachments.splice(attachmentIndex, 1);
            this.applicationsSubject.next([...this.applications]);
            observer.next(true);
          } else {
            observer.next(false);
          }
        } else {
          observer.next(false);
        }
        observer.complete();
      }, 500);
    });
  }

  // 獲取統計數據
  getStatistics(userId: string) {
    const userApps = this.getUserApplications(userId);
    return {
      total: userApps.length,
      draft: userApps.filter(app => app.status === 'draft').length,
      submitted: userApps.filter(app => app.status === 'submitted').length,
      underReview: userApps.filter(app => app.status === 'under_review').length,
      approved: userApps.filter(app => app.status === 'approved').length,
      rejected: userApps.filter(app => app.status === 'rejected').length,
      completed: userApps.filter(app => app.status === 'completed').length
    };
  }
}
