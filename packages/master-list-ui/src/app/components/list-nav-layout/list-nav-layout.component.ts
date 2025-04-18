import { Component } from '@angular/core';
import { NavListComponent } from '../nav-list/nav-list.component';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet } from '@angular/router';
// import { NavListApiService } from '../../services/nav-list-api.service';
import { TagApiService } from '../../services/tag-api';

@Component({
    selector: 'app-list-nav-layout',
    imports: [NavListComponent, CommonModule, RouterOutlet],
    templateUrl: './list-nav-layout.component.html',
    styleUrl: './list-nav-layout.component.scss',
})
export class ListNavLayoutComponent {
    public activeListTab: 'note' | 'tag' = 'note';

    constructor(
        private listApi: TagApiService,
        private router: Router,
    ) {}

    ngOnInit() {
        // if (this.activeListTab === 'note') {
        //     this.listApi.getNotes(null, 0, 10).subscribe({ next: lists => {} });
        // } else {
            this.listApi.getTags(null, 0, 10).subscribe({
                next: lists => {},
            });
        // }
    }
    public updateListType(type: 'note' | 'tag') {
        this.activeListTab = type;
    }
    // Create an entry in the Note table (maybe tag add+ button is hidden or disabled), createNote rturns the id, navigate to the new note page
    public createList(type: string) {
        this.listApi.createNote(type).subscribe({
            next: createResult => {
                this.router.navigate(['lists', createResult.data.id]);
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
}

export interface LoadList {
    listType: string;
    id: string;
}
