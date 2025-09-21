import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApplicationService, Application, ApplicationType, ProcessingSpeed, Attachment } from '../application';
import { Auth } from '../auth';

@Component({
  selector: 'app-application-form',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './application-form.html',
  styleUrl: './application-form.css'
})
export class ApplicationForm implements OnInit {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private applicationService = inject(ApplicationService);
  private auth = inject(Auth);

  applicationForm: FormGroup;
  isEditMode = false;
  existingApplication: Application | null = null;
  isLoading = false;
  uploadProgress: { [key: string]: number } = {};
  pendingAttachments: { type: string, files: File[] }[] = [];

  // 辦理類別選項
  applicationTypes: ApplicationType[] = ['首來族', '換證', '遺失件'];

  // 辦理速度選項
  processingSpeeds: ProcessingSpeed[] = ['急件', '普通件'];

  // 附件類型選項
  attachmentTypes = [
    '戶謄',
    '父親身分證',
    '母親身分證',
    '聲明書',
    '報案單',
    '舊台胞卡',
    '舊台胞證影本',
    '其他'
  ];

  constructor() {
    this.applicationForm = this.fb.group({
      type: ['', Validators.required],
      speed: ['普通件', Validators.required],
      applicationDate: [this.getTodayDate(), Validators.required],
      customerName: ['', [Validators.required, Validators.minLength(2)]]
    });
  }

  ngOnInit() {
    // 檢查是否有編輯模式
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras?.state?.['application']) {
      this.isEditMode = true;
      this.existingApplication = navigation.extras.state['application'];
      this.populateForm();
    }
  }

  private getTodayDate(): string {
    return new Date().toISOString().split('T')[0];
  }

  private populateForm() {
    if (this.existingApplication) {
      this.applicationForm.patchValue({
        type: this.existingApplication.type,
        speed: this.existingApplication.speed,
        applicationDate: this.existingApplication.applicationDate,
        customerName: this.existingApplication.customerName
      });
    }
  }

  onSubmit() {
    if (this.applicationForm.valid) {
      this.isLoading = true;

      const currentUser = this.auth.getCurrentUser();
      if (!currentUser) {
        this.router.navigate(['/login']);
        return;
      }

      const formValue = this.applicationForm.value;

      if (this.isEditMode && this.existingApplication) {
        // 更新現有申請
        this.applicationService.updateApplication(this.existingApplication.id, {
          type: formValue.type,
          speed: formValue.speed,
          applicationDate: formValue.applicationDate,
          customerName: formValue.customerName
        }).subscribe({
          next: () => {
            this.isLoading = false;
            this.router.navigate(['/dashboard']);
          },
          error: (error) => {
            console.error('Update application error:', error);
            this.isLoading = false;
          }
        });
      } else {
        // 創建新申請
        const newApplication = {
          applicantId: currentUser.username,
          applicantName: currentUser.name,
          type: formValue.type,
          speed: formValue.speed,
          applicationDate: formValue.applicationDate,
          customerName: formValue.customerName,
          attachments: []
        };

        this.applicationService.createApplication(newApplication).subscribe({
          next: (application) => {
            // 上傳待處理的附件
            if (this.pendingAttachments.length > 0) {
              let uploadCount = 0;
              const totalUploads = this.pendingAttachments.reduce((sum, pa) => sum + pa.files.length, 0);

              this.pendingAttachments.forEach(pa => {
                pa.files.forEach(file => {
                  const attachment: Omit<Attachment, 'id' | 'uploadDate'> = {
                    name: file.name,
                    type: pa.type as any,
                    file: file,
                    size: file.size
                  };

                  this.applicationService.uploadAttachment(application.id, attachment).subscribe({
                    next: () => {
                      uploadCount++;
                      if (uploadCount === totalUploads) {
                        this.isLoading = false;
                        this.pendingAttachments = [];
                        this.router.navigate(['/dashboard']);
                      }
                    },
                    error: (error) => {
                      console.error('Upload attachment error:', error);
                      uploadCount++;
                      if (uploadCount === totalUploads) {
                        this.isLoading = false;
                        this.pendingAttachments = [];
                        this.router.navigate(['/dashboard']);
                      }
                    }
                  });
                });
              });
            } else {
              this.isLoading = false;
              this.router.navigate(['/dashboard']);
            }
          },
          error: (error) => {
            console.error('Create application error:', error);
            this.isLoading = false;
          }
        });
      }
    } else {
      this.markFormGroupTouched();
    }
  }

  onFileSelected(event: any, attachmentType: string) {
    const files = event.target.files;
    if (files && files.length > 0) {
      if (this.isEditMode && this.existingApplication) {
        // 編輯模式：立即上傳到現有申請
        for (let i = 0; i < files.length; i++) {
          const file = files[i];

          // 檢查檔案大小（限制 10MB）
          if (file.size > 10 * 1024 * 1024) {
            alert(`檔案 ${file.name} 太大，請選擇小於 10MB 的檔案`);
            continue;
          }

          this.uploadProgress[file.name] = 0;

          // 模擬上傳進度
          const progressInterval = setInterval(() => {
            this.uploadProgress[file.name] += 10;
            if (this.uploadProgress[file.name] >= 100) {
              clearInterval(progressInterval);

              // 上傳完成
              const attachment: Omit<Attachment, 'id' | 'uploadDate'> = {
                name: file.name,
                type: attachmentType as any,
                file: file,
                size: file.size
              };

              this.applicationService.uploadAttachment(this.existingApplication!.id, attachment).subscribe({
                next: () => {
                  delete this.uploadProgress[file.name];
                },
                error: (error) => {
                  console.error('Upload attachment error:', error);
                  delete this.uploadProgress[file.name];
                }
              });
            }
          }, 100);
        }
      } else {
        // 新建模式：添加到待上傳列表
        for (let i = 0; i < files.length; i++) {
          const file = files[i];

          // 檢查檔案大小（限制 10MB）
          if (file.size > 10 * 1024 * 1024) {
            alert(`檔案 ${file.name} 太大，請選擇小於 10MB 的檔案`);
            continue;
          }

          this.uploadProgress[file.name] = 0;

          // 模擬上傳進度
          const progressInterval = setInterval(() => {
            this.uploadProgress[file.name] += 10;
            if (this.uploadProgress[file.name] >= 100) {
              clearInterval(progressInterval);

              // 添加到待上傳列表
              const existingType = this.pendingAttachments.find(pa => pa.type === attachmentType);
              if (existingType) {
                existingType.files.push(file);
              } else {
                this.pendingAttachments.push({ type: attachmentType, files: [file] });
              }

              delete this.uploadProgress[file.name];
            }
          }, 100);
        }
      }
    }
  }

  removePendingAttachment(paIndex: number, fileIndex: number) {
    if (this.pendingAttachments[paIndex]) {
      this.pendingAttachments[paIndex].files.splice(fileIndex, 1);
      if (this.pendingAttachments[paIndex].files.length === 0) {
        this.pendingAttachments.splice(paIndex, 1);
      }
    }
  }

  removeAttachment(attachmentId: string) {
    if (this.existingApplication) {
      this.applicationService.deleteAttachment(this.existingApplication.id, attachmentId).subscribe({
        next: () => {
          // 附件已刪除
        },
        error: (error) => {
          console.error('Delete attachment error:', error);
        }
      });
    }
  }

  getFileSizeString(size: number): string {
    if (size < 1024) return size + ' B';
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
    return (size / (1024 * 1024)).toFixed(1) + ' MB';
  }

  private markFormGroupTouched() {
    Object.keys(this.applicationForm.controls).forEach(key => {
      const control = this.applicationForm.get(key);
      control?.markAsTouched();
    });
  }

  cancel() {
    this.router.navigate(['/dashboard']);
  }

  getFieldError(fieldName: string): string {
    const control = this.applicationForm.get(fieldName);
    if (control?.errors && control.touched) {
      if (control.errors['required']) {
        return this.getFieldLabel(fieldName) + '為必填項目';
      }
      if (control.errors['minlength']) {
        return this.getFieldLabel(fieldName) + '至少需要' + control.errors['minlength'].requiredLength + '個字符';
      }
    }
    return '';
  }

  private getFieldLabel(fieldName: string): string {
    const labels: { [key: string]: string } = {
      type: '辦理類別',
      speed: '辦理速度',
      applicationDate: '辦理日期',
      customerName: '顧客姓名'
    };
    return labels[fieldName] || fieldName;
  }

  // 獲取上傳進度鍵
  getUploadProgressKeys(): string[] {
    return Object.keys(this.uploadProgress);
  }

  // 檢查是否有上傳進度
  hasUploadProgress(): boolean {
    return Object.keys(this.uploadProgress).length > 0;
  }
}
