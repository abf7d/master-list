import { Component, OnInit, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoadList } from '../list-nav-layout/list-nav-layout.component';
import { ActivatedRoute, Router } from '@angular/router';
import { ColorFactoryService } from '../../services/color-factory.service';
import { TagApiService } from '../../services/api/tag-api';
import { NoteProps, TagProps } from '../../types/response/response';
import { NoteApiService } from '../../services/api/note-api.service';

@Component({
    selector: 'ml-nav-list',
    imports: [CommonModule],
    templateUrl: './nav-list.component.html',
    styleUrl: './nav-list.component.scss',
})
export class NavListComponent implements OnInit {
    public activeListTab: 'note' | 'tag' = 'note';
    public activeItem: string | null = null;
    public noteItems: NoteProps[] = [];
    public listItems: NavTag[] = [];

    constructor(
        private tagApi: TagApiService,
        private noteApi: NoteApiService,
        private router: Router,
        private route: ActivatedRoute,
        private colorFactory: ColorFactoryService
    ) {}

    ngOnInit() {
        this.route.paramMap.subscribe(params => {
          let listId = params.get('id');
          let listType = params.get('listType');
          if (listId && listType) {
            const type = listType as 'note' | 'tag';
            this.getListItems(type);
            this.activeListTab = type;
            this.activeItem = listId;
          } else {
            this.activeListTab = 'note';
            this.activeItem = null;
            this.getListItems(this.activeListTab);
          }
        });
    }

    public changeListType(type: 'note' | 'tag') {
        this.getListItems(type);
    }

    public getListItems(type: 'note' | 'tag') {
        if (type === 'note') {
            this.noteApi.getNotes(null, 1, 100).subscribe({
                next: lists => {
                    this.noteItems = lists.data;
                    this.activeListTab = type;
                },
            });
        } else {
            this.tagApi.getTags(null, 1, 100).subscribe({
                next: lists => {
                    const listItems = lists.data.map(x => ({...x, color: this.colorFactory.getColor(x.order).backgroundcolor}))
                    this.listItems = listItems;
                    this.activeListTab = type;
                },
            });
        }
    }
    public loadListItem(id: string) {
        this.activeItem = id;
        this.router.navigate(['lists', this.activeListTab, id]);
    }

    public createList(type: 'note' | 'tag') {
        this.noteApi.createNote(type).subscribe({
            next: createResult => {
                this.router.navigate(['lists', this.activeListTab, createResult.data.id]);
            },
        });
    }
    public navToList(props: LoadList) {}

 }

export interface NavTag extends TagProps {
  color: string;
}