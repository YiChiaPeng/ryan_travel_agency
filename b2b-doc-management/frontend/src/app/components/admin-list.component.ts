import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-admin-list',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './admin-list.component.html',
})
export class AdminListComponent implements OnInit {
  companyFilter = '';
  dateFilter = '';
  uploads: any[] = [];
  constructor(private http: HttpClient) {}
  ngOnInit() {
    // try backend if token present
    const token = sessionStorage.getItem('token');
    if (token && this.http) {
      this.http.get('/api/records', { headers: { Authorization: `Bearer ${token}` } }).subscribe({
        next: (res: any) => {
          this.uploads = Array.isArray(res) ? res : [];
        },
        error: () => this.loadFromLocal()
      });
    } else {
      this.loadFromLocal();
    }
  }

  loadFromLocal() {
    this.uploads = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)!;
      if (key.startsWith('uploads_')) {
        const raw = localStorage.getItem(key) || '[]';
        const arr = JSON.parse(raw);
        this.uploads.push(...arr.map((a: any) => ({ ...a })));
      }
    }
  }
  markReturned(u: any) {
    const reason = prompt('輸入退件原因（可留空）');
    u.status = '退件';
    u.returnReason = reason;
    // persist back to the correct company's storage
    const company = u.company || u.company_name || 'unknown';
    const raw = localStorage.getItem(`uploads_${company}`) || '[]';
    const uploads = JSON.parse(raw);
    const idx = uploads.findIndex((x: any) => x.id === u.id);
    if (idx !== -1) {
      uploads[idx] = { ...uploads[idx], status: u.status, returnReason: reason };
      localStorage.setItem(`uploads_${company}`, JSON.stringify(uploads));
    }
    // in real app send notification
    alert('已標記退件並發通知 (mock)');
  }
}
