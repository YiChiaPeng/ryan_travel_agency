import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-b2b-new',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './b2b-new.component.html',
})
export class B2BNewComponent {
  form: any;
  maxFileSizeMB = 10;
  constructor(private fb: FormBuilder, private router: Router, private http: HttpClient) {
    this.form = this.fb.group({
      type: ['首來族'],
      speed: ['普通件'],
      date: [new Date().toISOString().slice(0, 10)],
      name: [''],
      files: [null]
    });
  }

  onFiles(event: any) {
    const files: FileList = event.target.files;
    const arr: any[] = [];
    for (let i = 0; i < files.length; i++) {
      const f = files.item(i)!;
      if (f.size / 1024 / 1024 > this.maxFileSizeMB) {
        alert(`檔案 ${f.name} 大於 ${this.maxFileSizeMB}MB`);
        return;
      }
      arr.push({ name: f.name, size: f.size });
    }
    this.form.patchValue({ files: arr });
  }

  submit() {
    const company = sessionStorage.getItem('b2b_company') || 'unknown';
    const payload = {
      company,
      type: this.form.value.type,
      speed: this.form.value.speed,
      date: this.form.value.date,
      name: this.form.value.name,
      files: this.form.value.files
    };
    // try backend first
  const token = sessionStorage.getItem('token');
  const opts = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
  this.http.post('/api/records', payload, opts).subscribe({
      next: (res: any) => {
        this.router.navigate(['/b2b/list']);
      },
      error: () => {
        // fallback to localStorage
        const raw = localStorage.getItem(`uploads_${company}`) || '[]';
        const uploads = JSON.parse(raw);
        uploads.push({ id: Date.now(), ...payload, status: '待審核' });
        localStorage.setItem(`uploads_${company}`, JSON.stringify(uploads));
        this.router.navigate(['/b2b/list']);
      }
    });
  }
}
