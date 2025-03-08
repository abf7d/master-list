import { Component, input, signal } from '@angular/core';
import { NavItem } from '../nav-list/nav-list.component';

@Component({
  selector: 'ml-nav-tile',
  imports: [],
  templateUrl: './nav-tile.component.html',
  styleUrl: './nav-tile.component.scss'
})
export class NavTileComponent {
  readonly itemInfo = input<NavItem>(); 

}
