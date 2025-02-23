import { Routes } from '@angular/router';
import { AuthorizedUserGuard } from '@master-list/auth';
import { LoginComponent } from './components/login/login.component';

export const routes: Routes = [
    // {
    //     path: '',
    //     redirectTo: '/home',
    //     pathMatch: 'full'
    // },
    {
        path: 'home',
        loadComponent: () => import('./components/home/home.component').then(m => m.HomeComponent)
    },
    {
        path: 'main',
        loadComponent: () => import('./components/master-layout/master-layout.component').then(m => m.MasterLayoutComponent),
        canActivate: [AuthorizedUserGuard],
    },
    {
        path: 'login',
        component: LoginComponent,
    },
];
