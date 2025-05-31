import { Component, effect, EventEmitter, input, Input, model, OnInit, output, Output } from '@angular/core';
import { TagButton, TagDelete, TagGroupOption, TagSelection, TagSelectionGroup } from '../../types/tag';
import { ColorFactoryService } from '../../services/color-factory.service';
import { Project } from '../../types/projtect';
import { CommonModule } from '@angular/common';
import { TagUpdate } from '../../types/tag/tag-update';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { TagApiService } from '../../services/tag-api';
import { ToastrService } from 'ngx-toastr';
import { FormsModule } from '@angular/forms';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';
import { TagProps } from '../../types/response/response';

@Component({
    selector: 'app-tag-picker',
    imports: [CommonModule, FormsModule, ClickOutsideDirective, RouterModule],
    templateUrl: './tag-picker.component.html',
    styleUrl: './tag-picker.component.scss',
})
export class TagPickerComponent implements OnInit {
    readonly unassignTag = output<string[]>();
    readonly assignTag = output<string>();
    readonly addTag = output<AddTag>();
    readonly removeTag = output<string>();
    readonly completeAdd = model<TagUpdate | TagUpdate[]>();
    readonly completeDelete = input<TagDelete>();
    readonly tags = model<TagSelection[]>([]);
    public matchedEntries: TagProps[] = [];
    public autoCompleteInput = '';
    public autoCloseMenuToggle = false;
    public uniqeName = false;
    public showDefaultMenu = false;
    public selectedTag: TagSelection | null = null;
    public showMoveMenu = false;

    @Input() allowAdd = true;
    public activeGroup: TagSelectionGroup | null = null;
    public isResourceView = true;
    public project!: Project;
    constructor(
        private colorFactory: ColorFactoryService,
        private route: ActivatedRoute,
        private toastr: ToastrService,
        private tagApi: TagApiService,
    ) {

        effect(() => {
            const newTag = this.completeAdd();
            if (Array.isArray(newTag)) {
                newTag.forEach(tag => {
                    this.handleAddTagComplete(tag);
                });
            } else if (newTag && typeof newTag === 'object') {
                this.handleAddTagComplete(newTag);
            }
        });

        // Effect to handle tag deletion completion
        effect(() => {
            const deletedTagName = this.completeDelete();
            if (deletedTagName) {
                this.handleDeleteTagComplete(deletedTagName.name);
            }
        });
    }
    public ngOnInit(): void {
        this.route.paramMap.subscribe(params => {
            this.tags.set([]);

            // Added below to clear the tags on route change, without this, previous route tags populate
            this.completeAdd.set([]);
        });
    }

    public filterTags = () => this.unassignTag.emit(this.tags().map(x => x.name));
    public removeAll = () => {
        const validNames = this.tags()
            .filter(x => x.isSelected)
            .map(x => x.name)
            .filter(x => x);
        console.log('validNames', validNames);
        if (validNames.length > 0) {
            this.unassignTag.emit(validNames);
        } else {
            this.toastr.warning('No tags selected', 'Nothing untagged');
        }
    };

    public assign() {
        const validNames = this.tags()
            .filter(x => x.isSelected)
            .map(x => x.name)
            .filter(x => x);
        if (validNames.length > 0) {
            this.assignTag.emit(validNames[0]);
        } else {
            this.toastr.warning('No tags selected', 'Nothing tagged');
        }
    }

    public select = (tag: TagSelection) => {
        tag.isSelected = !tag.isSelected;
        this.tags().forEach(x => {
            if (x.name !== tag.name) x.isSelected = false;
        });
        if (tag.isSelected) {
            this.selectedTag = tag;
        } else {
            this.selectedTag = null;
        }
    };

    private handleAddTagComplete(newUpdate: TagUpdate) {
        const name = newUpdate.name;
        const found = this.tags().find(x => x.name === name);
        if (found) {
            return;
        }
        const newTag = this.creatNewTag(newUpdate.name, newUpdate.id, 0, newUpdate.navId);
        this.tags().push(newTag);
    }

    public creatNewTag(name: string, nameIndex: number, groupIndex: number, navId?: string): TagSelection {
        const color = this.colorFactory.getColor(nameIndex);
        return {
            name,
            color: color.color,
            backgroundcolor: color.backgroundcolor,
            isSelected: false,
            navId: navId,
        };
    }
    private handleDeleteTagComplete(deleteName: string) {
        const tag = this.tags().find(x => x.name === deleteName);
        if (tag) {
            this.tags().splice(this.tags().indexOf(tag), 1);
        }
    }

    // this triggered removeGroup with a delete = true value
    public remove(tag: TagSelection) {
        this.removeTag.emit(tag.name);
    }
    // this triggered removeGroup with a delete = false value
    public excludeFromList = (tag: TagSelection) => {
        this.handleDeleteTagComplete(tag!.name);
    };

    public add(event: any, create = true, tag?: TagProps) {
        const name = event.value;
        if (this.tags().find(x => x.name === name)) {
            return;
        }
        // this.addGroup(name, tag, create);
        if (!create) {
          const tagUpdate: TagUpdate = { name: tag!.name, id: tag!.order, navId: tag!.id };
          this.handleAddTagComplete(tagUpdate);
        }
        this.addTag.emit({ name, tag, create });
        this.autoCompleteInput = '';
    }

    public autoComplete(currentValue: string) {
        this.autoCloseMenuToggle = false;
        console.log('currentValue', currentValue);
        this.matchedEntries = [];
        if (currentValue.length > 0) {
            this.showDefaultMenu = false;
            this.tagApi.getTags(currentValue, 1, 10).subscribe(tags => {
                console.log('matched tags', tags);
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
    public move() {}
    public archive() {}
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
