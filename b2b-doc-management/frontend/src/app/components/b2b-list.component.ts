import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-b2b-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './b2b-list.component.html',
})
export class B2BListComponent implements OnInit {
  company = '';
  uploads: any[] = [];
  constructor(private router: Router) {}
  ngOnInit() {
    this.company = sessionStorage.getItem('b2b_company') || '';
    // load mock uploads from localStorage for demo
    const raw = localStorage.getItem(`uploads_${this.company}`) || '[]';
    this.uploads = JSON.parse(raw);
  }
  newApplication() {
    this.router.navigate(['/b2b/new']);
  }
}
