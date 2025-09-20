import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Dashboard } from './dashboard/dashboard';
import { ApplicationForm } from './application-form/application-form';
import { ApplicationHistory } from './application-history/application-history';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'dashboard', component: Dashboard },
  { path: 'application-form', component: ApplicationForm },
  { path: 'application-form/:id', component: ApplicationForm },
  { path: 'application-history', component: ApplicationHistory },
  { path: '**', redirectTo: '/login' }
];