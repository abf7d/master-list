import { Routes } from '@angular/router';
import { AuthorizedUserGuard } from '@auth/gaurd/authorized-user.guard'; 
import { ErrorComponent } from '@lists/components/error/error.component';

export const routes: Routes = [
    {
        path: '',
        redirectTo: '/lists',
        pathMatch: 'full',
    },
    {
        path: 'home',
        loadComponent: () => import('@lists/components/home/home.component').then(m => m.HomeComponent),
    },
    {
        path: 'error',
        component: ErrorComponent
    },
    {
        path: 'lists',
        loadComponent: () => import('@lists/components/list-nav-layout/list-nav-layout.component').then(m => m.ListNavLayoutComponent),
        canActivate: [AuthorizedUserGuard], 
        children: [
            {
                path: '',
                loadComponent: () => import('@lists/components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            },
        ],
    },
    {
        path: 'lists/:listType/:id',
        loadComponent: () => import('@lists/components/list-nav-layout/list-nav-layout.component').then(m => m.ListNavLayoutComponent),
        canActivate: [AuthorizedUserGuard], 
        children: [
            {
                path: '',
                loadComponent: () => import('@lists/components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            },
        ]
    },
    {
        path: 'lists/:listType/:id/:page',
        loadComponent: () => import('@lists/components/list-nav-layout/list-nav-layout.component').then(m => m.ListNavLayoutComponent),
        canActivate: [AuthorizedUserGuard], 
        children: [
            {
                path: '',
                loadComponent: () => import('@lists/components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            },
        ]
    },
];
