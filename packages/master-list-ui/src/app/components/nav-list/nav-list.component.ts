import { Component, OnInit, output } from '@angular/core';
import { NavTileComponent } from '../nav-tile/nav-tile.component';
import { CommonModule } from '@angular/common';
import { TagApiService } from '../../services/tag-api';
import { LoadList } from '../list-nav-layout/list-nav-layout.component';

@Component({
  selector: 'ml-nav-list',
  imports: [CommonModule, NavTileComponent],
  templateUrl: './nav-list.component.html',
  styleUrl: './nav-list.component.scss'
})
export class NavListComponent implements OnInit {

  readonly createList = output<string>();
  readonly loadList = output<LoadList>();
  readonly updateListType = output<'note' | 'tag'>();

  public activeTab: 'note' | 'tag' = 'note';

  constructor(private tagApi: TagApiService) {}
  public ngOnInit() {
   
  }
  public addClicked(type: 'note' | 'tag') {
    this.createList.emit(type);
  }
  public listItemClicked(listType: 'note' | 'tag', id: string){
    this.loadList.emit({listType, id});
  }
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
    id: '2',
    order: 1
  }, {
    title: 'Note 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '3',
    order: 1
  }, {
    title: 'Note 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '4',
    order: 1
  }];
  public listItems: NavItem[] = [{
    title: 'List 1',
    content: 'This is text for the first note. It has sample text to make it longer.',
    updatedAt: '2 hours ago',
    created: '3/7/2025',
    id: '5',
    order: 1
  }, {
    title: 'List 1',
    content: 'Item 1, Itemd2, Item 3.',
    updatedAt: '3 hours ago',
    created: '3/7/2025',
    id: '6',
    order: 1
  }, {
    title: 'List 1',
    content: 'Item 1, Itemd2, Item 3.',
    updatedAt: '4 hours ago',
    created: '3/7/2025',
    id: '7',
    order: 1
  }, {
    title: 'List 1',
    content: 'Item 1, Itemd2, Item 3.',
    updatedAt: '5 hours ago',
    created: '3/7/2025',
    id: '8',
    order: 1
  }];
  items: NavItem[] = this.noteItems;
 
  selectTab(listType: 'note' | 'tag') {
    this.activeTab = listType;
    if(listType === 'note') {
      this.items = this.noteItems;
    }
    if(listType === 'tag') {
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
