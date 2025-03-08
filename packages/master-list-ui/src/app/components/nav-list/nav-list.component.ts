import { Component } from '@angular/core';
import { NavTileComponent } from '../nav-tile/nav-tile.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'ml-nav-list',
  imports: [CommonModule, NavTileComponent],
  templateUrl: './nav-list.component.html',
  styleUrl: './nav-list.component.scss'
})
export class NavListComponent {
  public noteItems: NavItem[] = [{
    title: 'Note 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }, {
    title: 'Note 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }, {
    title: 'Note 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }, {
    title: 'Note 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }];
  public listItems: NavItem[] = [{
    title: 'List 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '2 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }, {
    title: 'List 1',
    content: 'Item 1, Itemd2, Item 3.',
    updatedAt: '3 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }, {
    title: 'List 1',
    content: 'Item 1, Itemd2, Item 3.',
    updatedAt: '4 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }, {
    title: 'List 1',
    content: 'Item 1, Itemd2, Item 3.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '1',
    order: 1
  }];
  items: NavItem[] = this.noteItems;
  activeTab: 'notes' | 'lists' = 'notes';
  selectTab(listType: 'notes' | 'lists') {
    this.activeTab = listType;
    if(listType === 'notes') {
      this.items = this.noteItems;
    }
    if(listType === 'lists') {
      this.items = this.listItems;
    }
  }
}
export interface NavItem {
  title: string;
  content: string;
  updatedAt: string;
  created: string;
  id: string;
  order: number;
}
