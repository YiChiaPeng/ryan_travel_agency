import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './login.component.html',
})
export class LoginComponent {
  form: any;
  constructor(private fb: FormBuilder, private router: Router, private http: HttpClient) {
    this.form = this.fb.group({ company: [''], password: [''] });
  }
  submit() {
    const payload = { username: this.form.value.company, password: this.form.value.password };
    this.http.post('/api/login', payload).subscribe({
      next: (res: any) => {
        // store mock token/company
        sessionStorage.setItem('b2b_company', this.form.value.company);
        if (res && res.token) sessionStorage.setItem('token', res.token);
        this.router.navigate(['/b2b/list']);
      },
      error: () => {
        // fallback mock login
        sessionStorage.setItem('b2b_company', this.form.value.company);
        this.router.navigate(['/b2b/list']);
      }
    });
  }
}
