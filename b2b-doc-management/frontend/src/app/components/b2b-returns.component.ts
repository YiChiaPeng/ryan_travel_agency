import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-b2b-returns',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './b2b-returns.component.html',
})
export class B2BReturnsComponent implements OnInit {
  company = '';
  returned: any[] = [];
  constructor(private http: HttpClient) {}
  ngOnInit() {
    this.company = sessionStorage.getItem('b2b_company') || '';
    const raw = localStorage.getItem(`uploads_${this.company}`) || '[]';
    const uploads = JSON.parse(raw);
    this.returned = uploads.filter((u: any) => u.status === '退件');
  }

  onFiles(event: any, item: any) {
    const files: FileList = event.target.files;
    const arr: any[] = [];
    for (let i = 0; i < files.length; i++) {
      const f = files.item(i)!;
      arr.push({ name: f.name, size: f.size });
    }
    // attach resubmission files and mark as resubmitted
    const raw = localStorage.getItem(`uploads_${this.company}`) || '[]';
    const uploads = JSON.parse(raw);
    const idx = uploads.findIndex((u: any) => u === item || u.id === item.id);
    if (idx !== -1) {
      const payload = { files: arr };
  // try backend
  const token = sessionStorage.getItem('token');
  const opts = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
  this.http.post(`/api/record/${item.id}/resubmit`, payload, opts).subscribe({
        next: () => {
          alert('補件已送出（後端）');
          // update local view as well
          uploads[idx].resubmission = { files: arr, date: new Date().toISOString() };
          uploads[idx].status = '待審核';
          localStorage.setItem(`uploads_${this.company}`, JSON.stringify(uploads));
          this.returned = uploads.filter((u: any) => u.status === '退件');
        },
        error: () => {
          // fallback
          uploads[idx].resubmission = { files: arr, date: new Date().toISOString() };
          uploads[idx].status = '待審核';
          localStorage.setItem(`uploads_${this.company}`, JSON.stringify(uploads));
          this.returned = uploads.filter((u: any) => u.status === '退件');
          alert('補件已送出（demo）');
        }
      });
    }
  }
}
