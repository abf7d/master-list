import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        redirectTo: 'master',
        pathMatch: 'full'
    },
    {
        path: 'master',
        loadComponent: () => import('./components/master-layout/master-layout.component').then(m => m.MasterLayoutComponent)
    }
];
