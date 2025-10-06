import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApplicationService, Application, ApplicationType, ProcessingSpeed, Attachment } from '../application';
import { Auth } from '../auth';

interface IdCardImage {
  preview: string | null;
  file: File | null;
  scale: number;
  rotation: number;
  cropping: boolean;
  cropBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  originalPreview?: string;
  isDragging?: boolean;
  dragStart?: { x: number; y: number };
  isCropDragging?: boolean;
  cropDragStart?: { x: number; y: number };
  cropHandle?: string;
}

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
  isExtractingInfo = false; // OCR處理狀態
  uploadProgress: { [key: string]: number } = {};
  pendingAttachments: { type: string, files: File[] }[] = [];

  // 身分證圖片管理
  idCardImages: { front: IdCardImage, back: IdCardImage } = {
    front: {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 200, height: 120 }
    },
    back: {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 200, height: 120 }
    }
  };

  // 二寸照片圖片管理
  photoImages: { passport: IdCardImage } = {
    passport: {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 160, height: 200 } // 2吋照片比例 35mm x 45mm
    }
  };

  // 護照圖片管理
  passportImages: { front: IdCardImage } = {
    front: {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 280, height: 200 } // 護照頁面比例
    }
  };

  // 辦理類別選項
  applicationTypes: ApplicationType[] = ['首次申請', '換證', '遺失件'];

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
      customerName: ['', [Validators.required, Validators.minLength(2)]],
      // 個人詳細資料
      chineseLastName: ['', [Validators.required, Validators.minLength(1)]],
      chineseFirstName: ['', [Validators.required, Validators.minLength(1)]],
      englishLastName: ['', [Validators.required, Validators.minLength(1)]],
      englishFirstName: ['', [Validators.required, Validators.minLength(1)]],
      nationalId: ['', [Validators.required, Validators.pattern(/^[A-Z][12]\d{8}$/)]],
      gender: ['', Validators.required],
      birthDate: ['', Validators.required],
      address: ['', [Validators.required, Validators.minLength(5)]],
      city: ['', Validators.required],
      district: ['', Validators.required],
      // 圖片上傳
      idCardFront: ['', Validators.required],
      idCardBack: ['', Validators.required],
      passportPhoto: ['', Validators.required],
      passportFront: ['', Validators.required]
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
        customerName: this.existingApplication.customerName,
        // 個人詳細資料 (如果存在的話)
        chineseLastName: this.existingApplication.individual?.chinese_last_name || '',
        chineseFirstName: this.existingApplication.individual?.chinese_first_name || '',
        englishLastName: this.existingApplication.individual?.english_last_name || '',
        englishFirstName: this.existingApplication.individual?.english_first_name || '',
        nationalId: this.existingApplication.individual?.national_id || '',
        gender: this.existingApplication.individual?.gender || ''
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
      customerName: '顧客姓名',
      idCardFront: '身分證正面',
      idCardBack: '身分證反面',
      passportPhoto: '二寸照片',
      passportFront: '護照正面'
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

  // ===== 身分證圖片處理方法 =====

  // 選擇身分證圖片
  onIdCardImageSelected(event: any, side: 'front' | 'back') {
    const file = event.target.files[0];
    if (!file) return;

    // 檢查檔案類型
    if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
      alert('請選擇 JPG 或 PNG 格式的圖片檔案');
      return;
    }

    // 檢查檔案大小（限制 10MB）
    if (file.size > 10 * 1024 * 1024) {
      alert('圖片檔案太大，請選擇小於 10MB 的檔案');
      return;
    }

    // 讀取檔案並建立預覽
    const reader = new FileReader();
    reader.onload = (e) => {
      this.idCardImages[side] = {
        preview: e.target?.result as string,
        file: file,
        scale: 1,
        rotation: 0,
        cropping: false,
        cropBox: { x: 50, y: 50, width: 200, height: 120 }
      };
      
      // 更新表單驗證狀態
      this.applicationForm.get(`idCard${side.charAt(0).toUpperCase() + side.slice(1)}`)?.setValue(file.name);
    };
    reader.readAsDataURL(file);
  }

  // 拖拽相關方法
  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    (event.currentTarget as HTMLElement)?.classList.add('drag-over');
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    (event.currentTarget as HTMLElement)?.classList.remove('drag-over');
  }

  onDrop(event: DragEvent, side: 'front' | 'back') {
    event.preventDefault();
    event.stopPropagation();
    (event.currentTarget as HTMLElement)?.classList.remove('drag-over');

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const mockEvent = { target: { files } };
      this.onIdCardImageSelected(mockEvent, side);
    }
  }

  // 旋轉圖片
  rotateImage(side: 'front' | 'back') {
    this.idCardImages[side].rotation = (this.idCardImages[side].rotation + 90) % 360;
  }

  // 縮放圖片
  zoomImage(side: 'front' | 'back', delta: number) {
    const newScale = Math.max(0.5, Math.min(3, this.idCardImages[side].scale + delta));
    this.idCardImages[side].scale = newScale;
  }

  // 縮放滑桿改變
  onZoomChange(event: any, side: 'front' | 'back') {
    this.idCardImages[side].scale = parseFloat(event.target.value);
  }

  // 滾輪縮放
  onImageWheel(event: WheelEvent, side: 'front' | 'back') {
    event.preventDefault();
    const delta = event.deltaY > 0 ? -0.1 : 0.1;
    this.zoomImage(side, delta);
  }

  // 圖片拖拽開始
  onImageMouseDown(event: MouseEvent, side: 'front' | 'back') {
    if (this.idCardImages[side].cropping) return;
    
    this.idCardImages[side].isDragging = true;
    this.idCardImages[side].dragStart = { x: event.clientX, y: event.clientY };
    event.preventDefault();
  }

  // 圖片拖拽移動
  onImageMouseMove(event: MouseEvent, side: 'front' | 'back') {
    const image = this.idCardImages[side];
    
    if (image.isDragging && image.dragStart) {
      // 這裡可以實現圖片拖拽移動功能
      // 由於CSS transform的限制，這裡暫時省略具體實現
    }

    if (image.isCropDragging && image.cropDragStart) {
      // 裁切框拖拽邏輯
      const deltaX = event.clientX - image.cropDragStart.x;
      const deltaY = event.clientY - image.cropDragStart.y;
      
      if (image.cropHandle) {
        this.updateCropBox(side, image.cropHandle, deltaX, deltaY);
      }
    }
  }

  // 圖片拖拽結束
  onImageMouseUp(event: MouseEvent, side: 'front' | 'back') {
    this.idCardImages[side].isDragging = false;
    this.idCardImages[side].isCropDragging = false;
    this.idCardImages[side].cropHandle = undefined;
  }

  // 開始裁切
  cropImage(side: 'front' | 'back') {
    this.idCardImages[side].cropping = true;
    // 保存原始預覽用於取消操作
    this.idCardImages[side].originalPreview = this.idCardImages[side].preview || undefined;
  }

  // 取消裁切
  cancelCrop(side: 'front' | 'back') {
    this.idCardImages[side].cropping = false;
    if (this.idCardImages[side].originalPreview) {
      this.idCardImages[side].preview = this.idCardImages[side].originalPreview;
    }
  }

  // 確認裁切
  confirmCrop(side: 'front' | 'back') {
    const image = this.idCardImages[side];
    if (!image.preview || !image.file) return;

    // 創建canvas進行裁切
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      // 計算裁切區域
      const cropBox = image.cropBox;
      canvas.width = cropBox.width;
      canvas.height = cropBox.height;

      // 應用變換並裁切
      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((image.rotation * Math.PI) / 180);
      ctx.scale(image.scale, image.scale);
      
      ctx.drawImage(
        img,
        -cropBox.x - cropBox.width / 2,
        -cropBox.y - cropBox.height / 2
      );
      
      ctx.restore();

      // 將裁切結果轉換為blob並更新預覽
      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onload = (e) => {
            image.preview = e.target?.result as string;
            image.cropping = false;
            
            // 創建新的File對象
            const croppedFile = new File([blob], image.file?.name || 'cropped-image.jpg', {
              type: 'image/jpeg'
            });
            image.file = croppedFile;
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.9);
    };
    
    img.src = image.originalPreview || image.preview;
  }

  // 裁切控制點拖拽
  onCropHandleMouseDown(event: MouseEvent, side: 'front' | 'back', handle: string) {
    event.preventDefault();
    event.stopPropagation();
    
    this.idCardImages[side].isCropDragging = true;
    this.idCardImages[side].cropDragStart = { x: event.clientX, y: event.clientY };
    this.idCardImages[side].cropHandle = handle;
  }

  // 更新裁切框
  private updateCropBox(side: 'front' | 'back', handle: string, deltaX: number, deltaY: number) {
    const cropBox = this.idCardImages[side].cropBox;
    
    switch (handle) {
      case 'tl': // 左上角
        cropBox.x += deltaX;
        cropBox.y += deltaY;
        cropBox.width -= deltaX;
        cropBox.height -= deltaY;
        break;
      case 'tr': // 右上角
        cropBox.y += deltaY;
        cropBox.width += deltaX;
        cropBox.height -= deltaY;
        break;
      case 'bl': // 左下角
        cropBox.x += deltaX;
        cropBox.width -= deltaX;
        cropBox.height += deltaY;
        break;
      case 'br': // 右下角
        cropBox.width += deltaX;
        cropBox.height += deltaY;
        break;
    }
    
    // 限制最小尺寸
    cropBox.width = Math.max(50, cropBox.width);
    cropBox.height = Math.max(30, cropBox.height);
    
    // 更新拖拽起始點
    if (this.idCardImages[side].cropDragStart) {
      this.idCardImages[side].cropDragStart!.x += deltaX;
      this.idCardImages[side].cropDragStart!.y += deltaY;
    }
  }

  // 移除身分證圖片
  removeIdCardImage(side: 'front' | 'back') {
    this.idCardImages[side] = {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 200, height: 120 }
    };
    
    // 清除表單驗證
    this.applicationForm.get(`idCard${side.charAt(0).toUpperCase() + side.slice(1)}`)?.setValue('');
  }

  // ===== 二寸照片處理方法 =====

  // 選擇二寸照片
  onPhotoImageSelected(event: any, type: 'passport') {
    const file = event.target.files[0];
    if (!file) return;

    // 檢查檔案類型
    if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
      alert('請選擇 JPG 或 PNG 格式的圖片檔案');
      return;
    }

    // 檢查檔案大小（限制 10MB）
    if (file.size > 10 * 1024 * 1024) {
      alert('圖片檔案太大，請選擇小於 10MB 的檔案');
      return;
    }

    // 讀取檔案並建立預覽
    const reader = new FileReader();
    reader.onload = (e) => {
      this.photoImages[type] = {
        preview: e.target?.result as string,
        file: file,
        scale: 1,
        rotation: 0,
        cropping: false,
        cropBox: { x: 50, y: 50, width: 160, height: 200 }
      };
      
      // 更新表單驗證狀態
      this.applicationForm.get('passportPhoto')?.setValue(file.name);
    };
    reader.readAsDataURL(file);
  }

  // 旋轉二寸照片
  rotatePhotoImage(type: 'passport') {
    this.photoImages[type].rotation = (this.photoImages[type].rotation + 90) % 360;
  }

  // 縮放二寸照片
  zoomPhotoImage(type: 'passport', delta: number) {
    const newScale = Math.max(0.5, Math.min(3, this.photoImages[type].scale + delta));
    this.photoImages[type].scale = newScale;
  }

  // 二寸照片縮放滑桿改變
  onPhotoZoomChange(event: any, type: 'passport') {
    this.photoImages[type].scale = parseFloat(event.target.value);
  }

  // 二寸照片拖拽開始
  onPhotoImageMouseDown(event: MouseEvent, type: 'passport') {
    if (this.photoImages[type].cropping) return;
    
    this.photoImages[type].isDragging = true;
    this.photoImages[type].dragStart = { x: event.clientX, y: event.clientY };
    event.preventDefault();
  }

  // 二寸照片拖拽移動
  onPhotoImageMouseMove(event: MouseEvent, type: 'passport') {
    const image = this.photoImages[type];
    
    if (image.isDragging && image.dragStart) {
      // 這裡可以實現圖片拖拽移動功能
    }

    if (image.isCropDragging && image.cropDragStart) {
      // 裁切框拖拽邏輯
      const deltaX = event.clientX - image.cropDragStart.x;
      const deltaY = event.clientY - image.cropDragStart.y;
      
      if (image.cropHandle) {
        this.updatePhotoCropBox(type, image.cropHandle, deltaX, deltaY);
      }
    }
  }

  // 二寸照片拖拽結束
  onPhotoImageMouseUp(event: MouseEvent, type: 'passport') {
    this.photoImages[type].isDragging = false;
    this.photoImages[type].isCropDragging = false;
    this.photoImages[type].cropHandle = undefined;
  }

  // 開始裁切二寸照片
  cropPhotoImage(type: 'passport') {
    this.photoImages[type].cropping = true;
    this.photoImages[type].originalPreview = this.photoImages[type].preview || undefined;
  }

  // 取消裁切二寸照片
  cancelPhotoCrop(type: 'passport') {
    this.photoImages[type].cropping = false;
    if (this.photoImages[type].originalPreview) {
      this.photoImages[type].preview = this.photoImages[type].originalPreview;
    }
  }

  // 確認裁切二寸照片
  confirmPhotoCrop(type: 'passport') {
    const image = this.photoImages[type];
    if (!image.preview || !image.file) return;

    // 創建canvas進行裁切
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      const cropBox = image.cropBox;
      canvas.width = cropBox.width;
      canvas.height = cropBox.height;

      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((image.rotation * Math.PI) / 180);
      ctx.scale(image.scale, image.scale);
      
      ctx.drawImage(
        img,
        -cropBox.x - cropBox.width / 2,
        -cropBox.y - cropBox.height / 2
      );
      
      ctx.restore();

      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onload = (e) => {
            image.preview = e.target?.result as string;
            image.cropping = false;
            
            const croppedFile = new File([blob], image.file?.name || 'cropped-passport-photo.jpg', {
              type: 'image/jpeg'
            });
            image.file = croppedFile;
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.9);
    };
    
    img.src = image.originalPreview || image.preview;
  }

  // 更新二寸照片裁切框
  private updatePhotoCropBox(type: 'passport', handle: string, deltaX: number, deltaY: number) {
    const cropBox = this.photoImages[type].cropBox;
    
    switch (handle) {
      case 'tl':
        cropBox.x += deltaX;
        cropBox.y += deltaY;
        cropBox.width -= deltaX;
        cropBox.height -= deltaY;
        break;
      case 'tr':
        cropBox.y += deltaY;
        cropBox.width += deltaX;
        cropBox.height -= deltaY;
        break;
      case 'bl':
        cropBox.x += deltaX;
        cropBox.width -= deltaX;
        cropBox.height += deltaY;
        break;
      case 'br':
        cropBox.width += deltaX;
        cropBox.height += deltaY;
        break;
    }
    
    // 保持2寸照片比例 (35mm x 45mm ≈ 7:9)
    if (handle === 'tl' || handle === 'tr' || handle === 'bl' || handle === 'br') {
      const ratio = 160 / 200; // 寬高比
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        cropBox.height = cropBox.width / ratio;
      } else {
        cropBox.width = cropBox.height * ratio;
      }
    }
    
    cropBox.width = Math.max(80, cropBox.width);
    cropBox.height = Math.max(100, cropBox.height);
    
    if (this.photoImages[type].cropDragStart) {
      this.photoImages[type].cropDragStart!.x += deltaX;
      this.photoImages[type].cropDragStart!.y += deltaY;
    }
  }

  // 移除二寸照片
  removePhotoImage(type: 'passport') {
    this.photoImages[type] = {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 160, height: 200 }
    };
    
    this.applicationForm.get('passportPhoto')?.setValue('');
  }

  // ===== 護照圖片處理方法 =====

  // 選擇護照圖片
  onPassportImageSelected(event: any, side: 'front') {
    const file = event.target.files[0];
    if (!file) return;

    // 檢查檔案類型
    if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
      alert('請選擇 JPG 或 PNG 格式的圖片檔案');
      return;
    }

    // 檢查檔案大小（限制 10MB）
    if (file.size > 10 * 1024 * 1024) {
      alert('圖片檔案太大，請選擇小於 10MB 的檔案');
      return;
    }

    // 讀取檔案並建立預覽
    const reader = new FileReader();
    reader.onload = (e) => {
      this.passportImages[side] = {
        preview: e.target?.result as string,
        file: file,
        scale: 1,
        rotation: 0,
        cropping: false,
        cropBox: { x: 50, y: 50, width: 280, height: 200 }
      };
      
      // 更新表單驗證狀態
      this.applicationForm.get('passportFront')?.setValue(file.name);
    };
    reader.readAsDataURL(file);
  }

  // 旋轉護照圖片
  rotatePassportImage(side: 'front') {
    this.passportImages[side].rotation = (this.passportImages[side].rotation + 90) % 360;
  }

  // 縮放護照圖片
  zoomPassportImage(side: 'front', delta: number) {
    const newScale = Math.max(0.5, Math.min(3, this.passportImages[side].scale + delta));
    this.passportImages[side].scale = newScale;
  }

  // 護照圖片縮放滑桿改變
  onPassportZoomChange(event: any, side: 'front') {
    this.passportImages[side].scale = parseFloat(event.target.value);
  }

  // 護照圖片拖拽開始
  onPassportImageMouseDown(event: MouseEvent, side: 'front') {
    if (this.passportImages[side].cropping) return;
    
    this.passportImages[side].isDragging = true;
    this.passportImages[side].dragStart = { x: event.clientX, y: event.clientY };
    event.preventDefault();
  }

  // 護照圖片拖拽移動
  onPassportImageMouseMove(event: MouseEvent, side: 'front') {
    const image = this.passportImages[side];
    
    if (image.isDragging && image.dragStart) {
      // 這裡可以實現圖片拖拽移動功能
    }

    if (image.isCropDragging && image.cropDragStart) {
      // 裁切框拖拽邏輯
      const deltaX = event.clientX - image.cropDragStart.x;
      const deltaY = event.clientY - image.cropDragStart.y;
      
      if (image.cropHandle) {
        this.updatePassportCropBox(side, image.cropHandle, deltaX, deltaY);
      }
    }
  }

  // 護照圖片拖拽結束
  onPassportImageMouseUp(event: MouseEvent, side: 'front') {
    this.passportImages[side].isDragging = false;
    this.passportImages[side].isCropDragging = false;
    this.passportImages[side].cropHandle = undefined;
  }

  // 開始裁切護照圖片
  cropPassportImage(side: 'front') {
    this.passportImages[side].cropping = true;
    this.passportImages[side].originalPreview = this.passportImages[side].preview || undefined;
  }

  // 取消裁切護照圖片
  cancelPassportCrop(side: 'front') {
    this.passportImages[side].cropping = false;
    if (this.passportImages[side].originalPreview) {
      this.passportImages[side].preview = this.passportImages[side].originalPreview;
    }
  }

  // 確認裁切護照圖片
  confirmPassportCrop(side: 'front') {
    const image = this.passportImages[side];
    if (!image.preview || !image.file) return;

    // 創建canvas進行裁切
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      const cropBox = image.cropBox;
      canvas.width = cropBox.width;
      canvas.height = cropBox.height;

      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((image.rotation * Math.PI) / 180);
      ctx.scale(image.scale, image.scale);
      
      ctx.drawImage(
        img,
        -cropBox.x - cropBox.width / 2,
        -cropBox.y - cropBox.height / 2
      );
      
      ctx.restore();

      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onload = (e) => {
            image.preview = e.target?.result as string;
            image.cropping = false;
            
            const croppedFile = new File([blob], image.file?.name || 'cropped-passport.jpg', {
              type: 'image/jpeg'
            });
            image.file = croppedFile;
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.9);
    };
    
    img.src = image.originalPreview || image.preview;
  }

  // 更新護照圖片裁切框
  private updatePassportCropBox(side: 'front', handle: string, deltaX: number, deltaY: number) {
    const cropBox = this.passportImages[side].cropBox;
    
    switch (handle) {
      case 'tl':
        cropBox.x += deltaX;
        cropBox.y += deltaY;
        cropBox.width -= deltaX;
        cropBox.height -= deltaY;
        break;
      case 'tr':
        cropBox.y += deltaY;
        cropBox.width += deltaX;
        cropBox.height -= deltaY;
        break;
      case 'bl':
        cropBox.x += deltaX;
        cropBox.width -= deltaX;
        cropBox.height += deltaY;
        break;
      case 'br':
        cropBox.width += deltaX;
        cropBox.height += deltaY;
        break;
    }
    
    cropBox.width = Math.max(100, cropBox.width);
    cropBox.height = Math.max(70, cropBox.height);
    
    if (this.passportImages[side].cropDragStart) {
      this.passportImages[side].cropDragStart!.x += deltaX;
      this.passportImages[side].cropDragStart!.y += deltaY;
    }
  }

  // 移除護照圖片
  removePassportImage(side: 'front') {
    this.passportImages[side] = {
      preview: null,
      file: null,
      scale: 1,
      rotation: 0,
      cropping: false,
      cropBox: { x: 50, y: 50, width: 280, height: 200 }
    };
    
    this.applicationForm.get('passportFront')?.setValue('');
  }

  // ===== 專用拖拽和事件處理方法 =====

  // 二寸照片拖拽處理
  onPhotoDrop(event: DragEvent, type: 'passport') {
    event.preventDefault();
    event.stopPropagation();
    (event.currentTarget as HTMLElement)?.classList.remove('drag-over');

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const mockEvent = { target: { files } };
      this.onPhotoImageSelected(mockEvent, type);
    }
  }

  // 二寸照片滾輪事件
  onPhotoImageWheel(event: WheelEvent, type: 'passport') {
    event.preventDefault();
    const delta = event.deltaY > 0 ? -0.1 : 0.1;
    this.zoomPhotoImage(type, delta);
  }

  // 二寸照片裁切控制點
  onPhotoCropHandleMouseDown(event: MouseEvent, type: 'passport', handle: string) {
    event.preventDefault();
    event.stopPropagation();
    
    this.photoImages[type].isCropDragging = true;
    this.photoImages[type].cropDragStart = { x: event.clientX, y: event.clientY };
    this.photoImages[type].cropHandle = handle;
  }

  // 護照拖拽處理
  onPassportDrop(event: DragEvent, side: 'front') {
    event.preventDefault();
    event.stopPropagation();
    (event.currentTarget as HTMLElement)?.classList.remove('drag-over');

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      const mockEvent = { target: { files } };
      this.onPassportImageSelected(mockEvent, side);
    }
  }

  // 護照滾輪事件
  onPassportImageWheel(event: WheelEvent, side: 'front') {
    event.preventDefault();
    const delta = event.deltaY > 0 ? -0.1 : 0.1;
    this.zoomPassportImage(side, delta);
  }

  // 護照裁切控制點
  onPassportCropHandleMouseDown(event: MouseEvent, side: 'front', handle: string) {
    event.preventDefault();
    event.stopPropagation();
    
    this.passportImages[side].isCropDragging = true;
    this.passportImages[side].cropDragStart = { x: event.clientX, y: event.clientY };
    this.passportImages[side].cropHandle = handle;
  }

  // OCR + LLM 提取護照資訊
  async extractPassportInfo(side: 'front') {
    if (!this.passportImages[side].file) {
      alert('請先上傳護照圖片');
      return;
    }

    this.isExtractingInfo = true;

    try {
      // 1. 準備圖片數據
      const imageBase64 = await this.fileToBase64(this.passportImages[side].file!);
      
      // 2. 調用OCR API
      const ocrResult = await this.performOCR(imageBase64);
      
      // 3. 使用LLM解析OCR結果
      const extractedInfo = await this.parsePasportInfoWithLLM(ocrResult);
      
      // 4. 自動填入表單
      if (extractedInfo) {
        this.fillFormWithExtractedInfo(extractedInfo);
        alert('護照資訊提取成功！已自動填入表單。');
      } else {
        alert('未能提取到完整的護照資訊，請手動填寫。');
      }
      
    } catch (error) {
      console.error('護照資訊提取失敗:', error);
      alert('護照資訊提取失敗，請檢查圖片清晰度或手動填寫。');
    } finally {
      this.isExtractingInfo = false;
    }
  }

  // 將文件轉換為Base64
  private fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // 移除 data:image/...;base64, 前綴
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // 執行OCR
  private async performOCR(imageBase64: string): Promise<string> {
    try {
      const response = await fetch('/api/ocr/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.auth.getToken()}`
        },
        body: JSON.stringify({
          image: imageBase64,
          language: 'chi_tra+eng' // 繁體中文 + 英文
        })
      });

      if (!response.ok) {
        throw new Error(`OCR API 錯誤: ${response.statusText}`);
      }

      const data = await response.json();
      return data.text || '';
    } catch (error) {
      console.error('OCR 處理失敗:', error);
      throw error;
    }
  }

  // 使用LLM解析護照資訊
  private async parsePasportInfoWithLLM(ocrText: string): Promise<any> {
    try {
      const response = await fetch('/api/llm/extract-passport-info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.auth.getToken()}`
        },
        body: JSON.stringify({
          ocrText: ocrText
        })
      });

      if (!response.ok) {
        throw new Error(`LLM API 錯誤: ${response.statusText}`);
      }

      const data = await response.json();
      return data.result || null;
    } catch (error) {
      console.error('LLM 處理失敗:', error);
      throw error;
    }
  }

  // 將提取的資訊填入表單
  private fillFormWithExtractedInfo(info: any) {
    if (info.chineseLastName) {
      this.applicationForm.patchValue({ chineseLastName: info.chineseLastName });
    }
    if (info.chineseFirstName) {
      this.applicationForm.patchValue({ chineseFirstName: info.chineseFirstName });
    }
    if (info.englishLastName) {
      this.applicationForm.patchValue({ englishLastName: info.englishLastName });
    }
    if (info.englishFirstName) {
      this.applicationForm.patchValue({ englishFirstName: info.englishFirstName });
    }
    if (info.birthDate) {
      this.applicationForm.patchValue({ birthDate: info.birthDate });
    }
    if (info.gender && (info.gender === '男' || info.gender === '女')) {
      this.applicationForm.patchValue({ gender: info.gender });
    }
    if (info.nationalId) {
      this.applicationForm.patchValue({ nationalId: info.nationalId });
    }
  }
}
