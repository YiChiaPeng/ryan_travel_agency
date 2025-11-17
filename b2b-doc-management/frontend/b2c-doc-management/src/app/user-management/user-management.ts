import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';
import { Auth } from '../auth';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-management.html',
  styleUrl: './user-management.css'
})
export class UserManagement implements OnInit {
  private api = inject(ApiService);
  private auth = inject(Auth);
  private router = inject(Router);

  users: any[] = [];
  form: any = { username: '', password: '', company_name: '', email: '', role: 'user' };
  currentUser: any = null;
  resetPasswordUserId: number | null = null;
  resetPasswordForm: any = { newPassword: '', confirmPassword: '' };
  showResetPasswordModal: boolean = false;

  ngOnInit(): void {
    const me = this.auth.getCurrentUser();
    if (!me) { this.router.navigate(['/login']); return; }
    if (!me.is_admin) { this.router.navigate(['/dashboard']); return; }
    this.currentUser = me;
    this.refresh();
  }

  goBack() {
    this.router.navigate(['/dashboard']);
  }

  private token(): string {
    return this.auth.getToken() || '';
  }

  refresh() {
    this.api.getUsers(this.token()).subscribe({
      next: (res) => {
        this.users = res?.data || [];
      },
      error: (err) => console.error(err)
    });
  }

  create() {
    const payload = { ...this.form };
    this.api.createUser(this.token(), payload).subscribe({
      next: () => {
        this.form = { username: '', password: '', company_name: '', email: '', role: 'user' };
        this.refresh();
      },
      error: (err) => alert(err?.error?.detail || '新增失敗')
    });
  }

  save(u: any) {
    const payload: any = { role: u.role };
    this.api.updateUser(this.token(), u.id, payload).subscribe({
      next: () => this.refresh(),
      error: (err) => alert(err?.error?.detail || '更新失敗')
    });
  }

  remove(u: any) {
    if (!confirm(`確認刪除使用者 ${u.username} ?`)) return;
    this.api.deleteUser(this.token(), u.id).subscribe({
      next: () => this.refresh(),
      error: (err) => alert(err?.error?.detail || '刪除失敗')
    });
  }

  openResetPasswordModal(u: any) {
    this.resetPasswordUserId = u.id;
    this.resetPasswordForm = { newPassword: '', confirmPassword: '' };
    this.showResetPasswordModal = true;
  }

  closeResetPasswordModal() {
    this.showResetPasswordModal = false;
    this.resetPasswordUserId = null;
    this.resetPasswordForm = { newPassword: '', confirmPassword: '' };
  }

  resetPassword() {
    if (!this.resetPasswordUserId) return;
    
    if (this.resetPasswordForm.newPassword !== this.resetPasswordForm.confirmPassword) {
      alert('密碼確認不符，請重新輸入');
      return;
    }

    if (this.resetPasswordForm.newPassword.length < 6) {
      alert('密碼長度至少需要 6 個字元');
      return;
    }

    const payload = { password: this.resetPasswordForm.newPassword };
    this.api.updateUser(this.token(), this.resetPasswordUserId, payload).subscribe({
      next: () => {
        alert('密碼重設成功');
        this.closeResetPasswordModal();
        this.refresh();
      },
      error: (err) => alert(err?.error?.detail || '密碼重設失敗')
    });
  }

  getUsernameById(userId: number): string {
    const user = this.users.find(u => u.id === userId);
    return user ? user.username : '';
  }
}
