import { Component } from '@angular/core';
import { NavListComponent } from '../nav-list/nav-list.component';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { TagApiService } from '../../services/api/tag-api';

@Component({
    selector: 'app-list-nav-layout',
    imports: [NavListComponent, CommonModule, RouterOutlet],
    templateUrl: './list-nav-layout.component.html',
    styleUrl: './list-nav-layout.component.scss',
})
export class ListNavLayoutComponent {
}

export interface LoadList {
    listType: string;
    id: string;
}
