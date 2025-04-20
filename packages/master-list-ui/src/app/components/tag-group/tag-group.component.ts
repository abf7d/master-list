import { Component, EventEmitter, input, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { TagSelection } from '../../types/tag';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TagApiService, TagProps } from '../../services/tag-api';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';
import { ToastrService } from 'ngx-toastr';
// import { TagSelection } from '@critical-pass/project/types';

@Component({
    selector: 'app-tag-group',
    templateUrl: './tag-group.component.html',
    styleUrls: ['./tag-group.component.scss'],
    imports: [CommonModule, FormsModule, ClickOutsideDirective],
    // standalone: false,
})
export class TagGroupComponent implements OnInit {
    @Input() title!: string;
    @Input() nameAttr!: string;
    @Input() colorBucket!: string;
    @Input() multiselect: boolean = false;
    readonly tags = input<TagSelection[]>([]); //<TagSelection[]>{[]);
    @Input() description!: string;
    @Input() allowAdd = true;

    @Input() hideAssignLinks!: boolean;
    @Output() assignTags = new EventEmitter<string[]>();
    @Output() unassignTags = new EventEmitter<string[]>();
    @Output() selectTag = new EventEmitter<string>();
    @Output() removeTag = new EventEmitter<RemoveTag>();
    @Output() addTag = new EventEmitter<AddTag>();
    public newTag = '';
    public matchedEntries: TagProps[] = [];
    public isSearching = false;
    public autoCompleteInput = '';
    public uniqeName = false;
    public selectedIndex = 0;
    public autoCloseMenuToggle = false;
    public showDefaultMenu = false;
    constructor(private tagApi: TagApiService, private toastr: ToastrService) {}
    public assign = () => {
        const validNames = this.tags()
            .filter(x => x.isSelected)
            .map(x => x.name)
            .filter(x => x);
        if (validNames.length > 0) {
            this.assignTags.emit(validNames);
        } else {
            this.toastr.warning('No tags selected', 'Nothing tagged')
        }
    };
    public removeAll = () => {
        const validNames = this.tags()
            .filter(x => x.isSelected)
            .map(x => x.name)
            .filter(x => x);
        console.log('validNames', validNames)
        if (validNames.length > 0) {
            this.unassignTags.emit(validNames);
        } else {
            this.toastr.warning('No tags selected', 'Nothing untagged')
        }
    };
    public select = (tag: TagSelection) => {
        this.selectTag.emit(tag.name);
        if (!this.multiselect) {
            this.tags().forEach(x => {
                if (x.name !== tag.name) x.isSelected = false;
            });
        }
        tag.isSelected = !tag.isSelected;
    };
    public remove = (tag: TagSelection) => this.removeTag.emit({ tag, delete: true });
    public add(event: any, create = true, tag?: TagProps) {
        const name = event.value;
        if (this.tags().find(x => x.name === name)) {
            return;
        }
        this.addTag.emit({ name, tag, create });
        this.autoCompleteInput = '';
    }
    public filterTags = () => this.unassignTags.emit(this.tags().map(x => x.name));
    public ngOnInit(): void {}

    public autoComplete(currentValue: string) {
        //event: KeyboardEvent, previousValue: string) {
        // const key = event.key;
        // const isPrintable = key.length === 1 && /^[\w\d\s`~!@#$%^&*()_\-+={}[\]|\\:;"'<>,.?/]$/.test(key);

        // // if (key === 'Backspace' || key === 'Delete')
        // if (isPrintable) {
        //     const currentValue = previousValue + event.key;
        this.autoCloseMenuToggle = false;
        console.log('currentValue', currentValue);
        this.matchedEntries = [];
        if (currentValue.length > 0) {
            //2) {
            this.showDefaultMenu = false;
            this.tagApi.getTags(currentValue, 1, 10).subscribe(tags => {
                console.log('matched tags', tags);
                // this.matchedEntries = tags.data.map((y: any) => y.name);

                const map = new Map<string, boolean>(this.tags().map(t => [t.name, true]));
                this.matchedEntries = tags.data.filter(t => !map.get(t.name));
                this.uniqeName = !this.matchedEntries.map(t => t.name).includes(this.autoCompleteInput);
            });
            //     }
        } else {
            this.uniqeName = false;
            this.showDefaultMenu = true;
        }
    }
    public showTagMenu(tag: TagSelection) {
        this.tags().forEach(t => (t.showDelMenu = t.name !== tag.name ? false : !tag.showDelMenu));
    }
    public closeCreateMenu = () => (this.autoCloseMenuToggle = true);
    public closeDeleteMenu = (tag: TagSelection) => (tag.showDelMenu = false);
    public includeInList(tag: TagProps) {
        this.add({ value: tag.name }, false, tag);
        this.matchedEntries = this.matchedEntries.filter(t => t.name !== tag.name);
    }
    public excludeFromList = (tag: TagSelection) => {
        this.removeTag.emit({ tag, delete: false });
        // const filteredTags = this.tags().filter(t => t.name !== tag.name)
        // this.tags.set(filteredTags);
    };
}

export interface AddTag {
    name?: string;
    tag?: TagProps;
    create: boolean;
}
export interface RemoveTag {
    tag?: TagSelection;
    delete: boolean;
}
