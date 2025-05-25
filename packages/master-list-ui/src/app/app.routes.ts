import { Routes } from '@angular/router';
import { MsalGuard } from '@azure/msal-angular';
import { AuthorizedUserGuard } from '../../projects/auth/src/lib/gaurd/authorized-user.guard';
import { ErrorComponent } from './components/error/error.component';

export const routes: Routes = [
    {
        path: '',
        redirectTo: '/lists',
        pathMatch: 'full',
    },
    {
        path: 'home',
        loadComponent: () => import('./components/home/home.component').then(m => m.HomeComponent),
    },
    {
        path: 'error',
        component: ErrorComponent
    },
    // {
    //     path: 'main',
    //     loadComponent: () => import('./components/master-layout/master-layout.component').then(m => m.MasterLayoutComponent),
    //     canActivate: [AuthorizedUserGuard],
    // },
    // {
    //     path: 'main/:id',
    //     loadComponent: () => import('./components/master-layout/master-layout.component').then(m => m.MasterLayoutComponent),
    //     canActivate: [AuthorizedUserGuard],
    // },
    {
        path: 'lists',
        loadComponent: () => import('./components/list-nav-layout/list-nav-layout.component').then(m => m.ListNavLayoutComponent),
        canActivate: [AuthorizedUserGuard], //[MsalGuard], //[
        children: [
            {
                path: '',
                loadComponent: () => import('./components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            },
            // {
            //     path: 'note',
            //     loadComponent: () => import('./components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            // },
            // {
            //     path: 'tag',
            //     loadComponent: () => import('./components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            // },
        ],
    },
    {
        path: 'lists/:listType/:id',
        loadComponent: () => import('./components/list-nav-layout/list-nav-layout.component').then(m => m.ListNavLayoutComponent),
        canActivate: [AuthorizedUserGuard], // [MsalGuard], //
        children: [
            {
                path: '',
                loadComponent: () => import('./components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            },
            // {
            //     path: 'note',
            //     loadComponent: () => import('./components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            // },
            // {
            //     path: 'tag',
            //     loadComponent: () => import('./components/list-editor/list-editor.component').then(m => m.ListEditorComponent),
            // },
        ]
    },
];
