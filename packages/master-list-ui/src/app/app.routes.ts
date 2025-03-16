import { Routes } from '@angular/router';
import { MsalGuard } from '@azure/msal-angular';

export const routes: Routes = [
    {
        path: '',
        redirectTo: '/main',
        pathMatch: 'full'
    },
    {
        path: 'home',
        loadComponent: () => import('./components/home/home.component').then(m => m.HomeComponent)
    },
    {
        path: 'main',
        loadComponent: () => import('./components/master-layout/master-layout.component').then(m => m.MasterLayoutComponent),
        canActivate: [MsalGuard],
    },
];
