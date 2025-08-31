import { Routes } from '@angular/router';
import { authGuard, adminGuard } from './guards/auth.guard';

export const routes: Routes = [
	{ path: '', redirectTo: 'login', pathMatch: 'full' },
	{ path: 'login', loadComponent: () => import('./components/login.component').then(m => m.LoginComponent) },
	{ path: 'b2b/list', loadComponent: () => import('./components/b2b-list.component').then(m => m.B2BListComponent), canActivate: [authGuard] },
	{ path: 'b2b/new', loadComponent: () => import('./components/b2b-new.component').then(m => m.B2BNewComponent), canActivate: [authGuard] },
	{ path: 'b2b/returns', loadComponent: () => import('./components/b2b-returns.component').then(m => m.B2BReturnsComponent), canActivate: [authGuard] },
	{ path: 'admin', loadComponent: () => import('./components/admin-list.component').then(m => m.AdminListComponent), canActivate: [adminGuard] }
];
