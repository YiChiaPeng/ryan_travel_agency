import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Auth, User } from '../auth';

@Component({
  selector: 'app-account-settings',
  imports: [CommonModule, FormsModule],
  templateUrl: './account-settings.html',
  styleUrl: './account-settings.css'
})
export class AccountSettings implements OnInit {
  private auth = inject(Auth);
  private router = inject(Router);

  currentUser: User | null = null;
  
  // 密碼修改表單
  passwordForm = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };

  // 個人資料表單
  profileForm = {
    name: '',
    email: ''
  };

  // 表單狀態
  isChangingPassword = false;
  isUpdatingProfile = false;
  passwordError = '';
  profileError = '';
  successMessage = '';

  ngOnInit() {
    if (!this.auth.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }

    this.currentUser = this.auth.getCurrentUser();
    if (this.currentUser) {
      this.profileForm.name = this.currentUser.name;
      this.profileForm.email = this.currentUser.email || '';
    }
  }

  // 驗證密碼格式
  validatePassword(password: string): boolean {
    return password.length >= 6;
  }

  // 修改密碼
  changePassword() {
    this.passwordError = '';
    this.successMessage = '';

    // 驗證表單
    if (!this.passwordForm.currentPassword) {
      this.passwordError = '請輸入目前密碼';
      return;
    }

    if (!this.validatePassword(this.passwordForm.newPassword)) {
      this.passwordError = '新密碼至少需要 6 個字元';
      return;
    }

    if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
      this.passwordError = '新密碼與確認密碼不符';
      return;
    }

    if (this.passwordForm.currentPassword === this.passwordForm.newPassword) {
      this.passwordError = '新密碼不能與目前密碼相同';
      return;
    }

    this.isChangingPassword = true;

    // 模擬 API 呼叫
    setTimeout(() => {
      try {
        // 這裡應該呼叫實際的 API
        this.successMessage = '密碼修改成功！';
        this.resetPasswordForm();
      } catch (error) {
        this.passwordError = '密碼修改失敗，請稍後再試';
      } finally {
        this.isChangingPassword = false;
      }
    }, 1000);
  }

  // 更新個人資料
  updateProfile() {
    this.profileError = '';
    this.successMessage = '';

    // 驗證表單
    if (!this.profileForm.name.trim()) {
      this.profileError = '請輸入姓名';
      return;
    }

    if (!this.profileForm.email.trim()) {
      this.profileError = '請輸入電子郵件';
      return;
    }

    if (!this.isValidEmail(this.profileForm.email)) {
      this.profileError = '請輸入有效的電子郵件格式';
      return;
    }

    this.isUpdatingProfile = true;

    // 模擬 API 呼叫
    setTimeout(() => {
      try {
        // 這裡應該呼叫實際的 API
        if (this.currentUser) {
          this.currentUser.name = this.profileForm.name;
          this.currentUser.email = this.profileForm.email;
          // 更新本地存儲
          localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
        }
        this.successMessage = '個人資料更新成功！';
      } catch (error) {
        this.profileError = '個人資料更新失敗，請稍後再試';
      } finally {
        this.isUpdatingProfile = false;
      }
    }, 1000);
  }

  // 驗證 email 格式
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // 重置密碼表單
  private resetPasswordForm() {
    this.passwordForm = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
  }

  // 返回儀表板
  goBack() {
    this.router.navigate(['/dashboard']);
  }

  // 清除訊息
  clearMessages() {
    this.passwordError = '';
    this.profileError = '';
    this.successMessage = '';
  }
}