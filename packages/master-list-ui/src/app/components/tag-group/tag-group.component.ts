import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { TagSelection } from '../../types/tag';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
// import { TagSelection } from '@critical-pass/project/types';

@Component({
    selector: 'app-tag-group',
    templateUrl: './tag-group.component.html',
    styleUrls: ['./tag-group.component.scss'],
    imports: [CommonModule, FormsModule]
    // standalone: false,
})
export class TagGroupComponent implements OnInit {
    @Input() title!: string;
    @Input() nameAttr!: string;
    @Input() colorBucket!: string;
    @Input() multiselect: boolean = false;
    @Input() tags: TagSelection[] = [];
    @Input() description!: string;
    @Input() allowAdd = true;

    @Input() hideAssignLinks!: boolean;
    @Output() assignTags = new EventEmitter<string[]>();
    @Output() unassignTags = new EventEmitter<string>();
    @Output() selectTag = new EventEmitter<string>();
    @Output() removeTag = new EventEmitter<TagSelection>();
    @Output() addTag = new EventEmitter<string>();
    public newTag = '';
    constructor() {}
    public assign = () => this.assignTags.emit(this.tags.filter(x => x.isSelected).map(x => x.name));
    public removeAll = () => this.unassignTags.emit();
    public select = (tag: TagSelection) => {
        this.selectTag.emit(tag.name);
        if (!this.multiselect) {
            this.tags.forEach(x => {
                if (x.name !== tag.name) x.isSelected = false;
            });
        }
        tag.isSelected = !tag.isSelected;
    };
    public remove = (tag: TagSelection) => this.removeTag.emit(tag);
    public add(event: any) {
        const name = event.value;
        if (this.tags.find(x => x.name === name)) {
            return;
        }
        this.addTag.emit(name);
        this.newTag = '';
    }
    public filterTags(): void {}
    public ngOnInit(): void {}
}
