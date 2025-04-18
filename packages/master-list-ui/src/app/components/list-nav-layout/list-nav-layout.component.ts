import { Component } from '@angular/core';
import { NavListComponent } from '../nav-list/nav-list.component';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-list-nav-layout',
  imports: [NavListComponent, CommonModule, RouterOutlet],
  templateUrl: './list-nav-layout.component.html',
  styleUrl: './list-nav-layout.component.scss'
})
export class ListNavLayoutComponent {

}
