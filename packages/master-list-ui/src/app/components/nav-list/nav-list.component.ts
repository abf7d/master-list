import { Component, OnInit, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NoteProps, TagApiService, TagProps, TagSearch } from '../../services/tag-api';
import { LoadList } from '../list-nav-layout/list-nav-layout.component';
import { ActivatedRoute, Router } from '@angular/router';
import { ColorFactoryService } from '../../services/color-factory.service';

@Component({
    selector: 'ml-nav-list',
    imports: [CommonModule],
    templateUrl: './nav-list.component.html',
    styleUrl: './nav-list.component.scss',
})
export class NavListComponent implements OnInit {
    public activeListTab: 'note' | 'tag' = 'note';
    public activeItem: string | null = null;

    constructor(
        private listApi: TagApiService,
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
            this.listApi.getNotes(null, 1, 100).subscribe({
                next: lists => {
                    // this.items = this.noteItems;
                    // const noteProps[] = lists.data;
                    this.noteItems = lists.data;
                    this.activeListTab = type;
                    // this.items = lists;
                },
            });
        } else {
            this.listApi.getTags(null, 1, 100).subscribe({
                next: lists => {
                    // this.items = this.listItems;
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
        this.listApi.createNote(type).subscribe({
            next: createResult => {
                this.router.navigate(['lists', this.activeListTab, createResult.data.id]);
                // Need to add listType to route parameters in route
                // navigate to page with neew id
                // router.navigate(`list/${props.listType}/${props.id}`);

                // need to update the left hand list with the new empty entry
                // have the title for that entry update when the note info is altered
                // need a place for the note name on the right hand side
            },
        });
    }
    public navToList(props: LoadList) {
        // Need to add listType to route parameters in route
        // navigate to teh lsit with the id
        // this.router.navigate(`/list/${props.listType}/${props.d}`)
    }

    // public addClicked(type: 'note' | 'tag') {
    //   this.createList.emit(type);
    // }
    // public loadListItem(listType: 'note' | 'tag', id: string) {
    //     this.loadList.emit({ listType, id });
    // }
    public noteItems: NoteProps[] = [];
    // = [
    //     {
    //         title: 'Note 1',
    //         description: 'This is text for the first note. It has sample text to make it longer.',
    //         updated_at: '5 hours ago',
    //         create_at: '3/7/2025',
    //         id: '1',
    //         order: 1,
    //     },
    //     {
    //         title: 'Note 1',
    //         content: 'This is text for the first note. It has sample text to make it longer.',
    //         updatedAt: '5 hours ago',
    //         created: '3/7/2025',
    //         id: '2',
    //         order: 1,
    //     },
    //     {
    //         title: 'Note 1',
    //         content: 'This is text for the first note. It has sample text to make it longer.',
    //         updatedAt: '5 hours ago',
    //         created: '3/7/2025',
    //         id: '3',
    //         order: 1,
    //     },
    //     {
    //         title: 'Note 1',
    //         content: 'This is text for the first note. It has sample text to make it longer.',
    //         updatedAt: '5 hours ago',
    //         created: '3/7/2025',
    //         id: '4',
    //         order: 1,
    //     },
    // ];
    public listItems: NavTag[] = [];
    //     {
    //         title: 'List 1',
    //         content: 'This is text for the first note. It has sample text to make it longer.',
    //         updatedAt: '2 hours ago',
    //         created: '3/7/2025',
    //         id: '5',
    //         order: 1,
    //     },
    //     {
    //         title: 'List 1',
    //         content: 'Item 1, Itemd2, Item 3.',
    //         updatedAt: '3 hours ago',
    //         created: '3/7/2025',
    //         id: '6',
    //         order: 1,
    //     },
    //     {
    //         title: 'List 1',
    //         content: 'Item 1, Itemd2, Item 3.',
    //         updatedAt: '4 hours ago',
    //         created: '3/7/2025',
    //         id: '7',
    //         order: 1,
    //     },
    //     {
    //         title: 'List 1',
    //         content: 'Item 1, Itemd2, Item 3.',
    //         updatedAt: '5 hours ago',
    //         created: '3/7/2025',
    //         id: '8',
    //         order: 1,
    //     },
    // ];
    // items: NavItem[] = this.noteItems;

    // Create an entry in the Note table (maybe tag add+ button is hidden or disabled), createNote rturns the id, navigate to the new note page
}

export interface NavTag extends TagProps {
  color: string;
}