import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const token = sessionStorage.getItem('token');
  if (token) return true;
  return router.parseUrl('/login');
};

export const adminGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const token = sessionStorage.getItem('token');
  if (!token) return router.parseUrl('/login');
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (payload && payload.is_admin && payload.is_admin === 1) return true;
  } catch (e) {
    // ignore
  }
  return router.parseUrl('/login');
};
