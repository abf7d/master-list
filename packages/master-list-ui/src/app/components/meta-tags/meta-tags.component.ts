import { Component, effect, EventEmitter, input, Input, output, Output } from '@angular/core';
import { TagButton, TagDelete, TagGroupOption, TagSelection, TagSelectionGroup } from '../../types/tag';
import { ColorFactoryService } from '../../services/color-factory.service';
import { TagManagerService } from '../../services/tag-manager.service';
import { Project } from '../../types/projtect';
import { CommonModule } from '@angular/common';
import { AddTag, RemoveTag, TagGroupComponent } from '../tag-group/tag-group.component';
import { TagCssGenerator } from '../../services/tag-css-generator';
import { TagUpdate } from '../../types/tag/tag-update';

@Component({
    selector: 'app-meta-tags',
    imports: [CommonModule, TagGroupComponent],
    templateUrl: './meta-tags.component.html',
    styleUrl: './meta-tags.component.scss',
})
export class MetaTagsComponent {
    // @Output() assignTag = new EventEmitter<string>();
    // @Output() unAssignTag = new EventEmitter<string>();
    // @Input() tags: TagButton[] = [];
    readonly unAssignTag = output<string>();
    readonly assignTag = output<string>();
    // readonly tags = input<TagButton[]>([])
    readonly tagGroups = input<TagSelectionGroup>({ name: 'Tag Group', tags: [] }); //({ name: 'Tag Group', tags: [] })
    readonly addTag = output<AddTag>();
    readonly removeTag = output<string>();

    readonly completeAdd = input<TagUpdate>();
    readonly completeDelete = input<TagDelete>();

    @Input() allowAdd = true;
    // public tagGroups: TagSelectionGroup;
    public availableGroups: TagSelectionGroup[] = [];
    public activeGroup: TagSelectionGroup | null = null;
    public isResourceView = true;
    public project!: Project;
    // tags are passed in to create the selecable buttons. You can create new buttons which
    // should create new tags. These need to be shared with the top level so new tag name/color
    // combinations can translate to new tag circles or highlight text with the tags get
    // generated
    constructor(
        private colorFactory: ColorFactoryService,
        private metaTagService: TagManagerService,
        private tagNameColor: TagCssGenerator,
    ) {
        // this.id = +route.snapshot.params['id'];
        // this.project$ = this.dashboard.activeProject$;
        // const focusTag = this.creatNewTag('Focus', 0, 0); // high priority
        // const backgroundTag = this.creatNewTag('Background', 1, 0); // low prioritiy
        // const storageTag = this.creatNewTag('Storage', 2, 0);
        // const deleteTag = this.creatNewTag('Delete', 3, 0);
        // this.tagGroups = { name: 'Tag Group', tags: [] };
        this.availableGroups = [];

        this.project = {
            name: 'Test Project',
            description: 'Test Description',
            id: '1',
            tags: [],
            activities: [],
            profile: {
                view: {
                    selectedTagGroup: null,
                },
            },
        };
        // this.addGroup('Critical Pass');
        // this.addGroup('Work')
        // this.addGroup('Misc Triage');
        console.log(this.tagGroups());
        // this.addGroup('Focus');
        // this.addGroup('Background');
        // this.addGroup('Storage');
        // this.addGroup('Delete');

        effect(() => {
            const newTag = this.completeAdd();
            if (newTag) {
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
        // this.subscription = this.project$.pipe(filter(x => !!x)).subscribe(project => {
        //     if (project !== this.project) {
        //         const tagInfo: TagLoad = { tags: [], groups: [], activeGroup: null };
        //         this.metaTagService.loadTags(project, tagInfo);
        //         this.tagGroups.tags = tagInfo.tags;
        //         this.availableGroups = tagInfo.groups;
        //         this.activeGroup = tagInfo.activeGroup;
        //     }
        //     this.project = project;
        // });
        // this.tagNameColor.initTagColors(this.tagGroups())
    }
    public ngOnDestroy(): void {
        // this.subscription?.unsubscribe();
    }
    // public assignToActivities(tags: string[]) {
    //   this.metaTagService.assignTagsToSelectedActivities(
    //     this.project,
    //     tags,
    //     this.activeGroup!
    //   );
    //   // this.dashboard.updateProject(this.project, true);
    // }
    // public unassignFromActivities() {
    //   this.metaTagService.unassignFromActivities(
    //     this.activeGroup!.name,
    //     this.project
    //   );
    //   // this.dashboard.updateProject(this.project, true);
    // }
    // public selectTag(resource: any) {
    //   const type = 'resource';
    // }
    // public removeTag(tag: TagSelection) {
    //   if (
    //     this.activeGroup !== null &&
    //     this.project !== undefined &&
    //     this.project.tags !== undefined
    //   ) {
    //     this.activeGroup.tags.splice(this.activeGroup.tags.indexOf(tag), 1);
    //     const index = this.project.tags
    //       .find((x) => x.name === this.activeGroup!.name)
    //       ?.tags.indexOf(tag);
    //     if (index && index > -1) {
    //       this.project.tags
    //         .find((x) => x.name === this.activeGroup!.name)
    //         ?.tags.splice(index, 1);
    //     }
    //     this.metaTagService.removeTagFromActivities(
    //       this.project,
    //       this.activeGroup.name,
    //       tag
    //     );
    //     // this.dashboard.updateProject(this.project, true);
    //   }
    // }
    // public addTag(name: any) {
    //   if (this.activeGroup !== null) {
    //     const schemeIndex = this.availableGroups.indexOf(this.activeGroup) + 2;
    //     const newTag = this.creatNewTag(
    //       name,
    //       this.activeGroup.tags.length,
    //       schemeIndex
    //     );
    //     this.activeGroup.tags.push(newTag);
    //     if (this.project.tags) {
    //       this.project.tags
    //         .find((x) => x.name === this.activeGroup!.name)
    //         ?.tags.push(newTag);
    //       // this.dashboard.updateProject(this.project, true);
    //     }
    //   }
    // }
    public selectGroup(name: any) {
        if (this.project.profile.view.selectedTagGroup === name) {
            this.project.profile.view.selectedTagGroup = null;
            this.activeGroup = null;
        } else {
            const activeGroup = this.availableGroups.find(x => x.name === name);
            if (activeGroup) {
                this.activeGroup = activeGroup;
            }
            this.project.profile.view.selectedTagGroup = name;
        }
        // this.dashboard.updateProject(this.project, true);
        // this.assignTag.emit(name);
    }
    public unassignGroup(name: string) {
        this.unAssignTag.emit(name);
    }
    public assignGroup(name: string[]) {
        this.assignTag.emit(name[0]);
    }

    private handleAddTagComplete(newUpdate: TagUpdate) {
        const name = newUpdate.name;
        const newTag = this.creatNewTag(newUpdate.name, newUpdate.id, 0);
        // const newTag = this.creatNewTag(newUpdate.name, this.tagGroups().tags.length, 0);
        this.tagGroups().tags.push(newTag);

        const newSelectionGroup: TagSelectionGroup = { name, tags: [] };
        this.availableGroups.push(newSelectionGroup);

        const newTagGroupOption: TagGroupOption = {
            name,
            tags: [],
            color: newTag.color,
            backgroundcolor: newTag.backgroundcolor,
        };
        this.metaTagService.addTagGroupToProject(this.project, newTagGroupOption);

        // This sends to master list so the color can be added to map for page
        const formatedTag: TagSelection = {
            name,
            color: newTag.color,
            backgroundcolor: newTag.backgroundcolor,
            isSelected: false,
        };
    }
    private handleDeleteTagComplete(deleteName: string) {
        const tag = this.tagGroups().tags.find(x => x.name === deleteName);
        if (tag) {
            this.tagGroups().tags.splice(this.tagGroups().tags.indexOf(tag), 1);
            const groupIndex = this.availableGroups.findIndex(x => x.name === tag.name);

            if (groupIndex > -1) {
                this.metaTagService.removeTagGroupFromProject(this.project, tag);
                this.availableGroups.splice(groupIndex, 1);
            }
        }
    }

    public removeGroup(tag: RemoveTag) {
        if (!tag.delete) {
            this.handleDeleteTagComplete(tag.tag!.name);
        }
        // this.tagGroups().tags.splice(this.tagGroups().tags.indexOf(tag), 1);
        // const groupIndex = this.availableGroups.findIndex(
        //   (x) => x.name === tag.name
        // );

        // if (groupIndex > -1) {
        //   this.metaTagService.removeTagGroupFromProject(this.project, tag);
        //   this.availableGroups.splice(groupIndex, 1);
        // }
        // This sends to master list to remove from map and page
        else {
            this.removeTag.emit(tag.tag!.name);
        }
        // this.dashboard.updateProject(this.project, true);
    }
    // Add tag should include an id so the color can be tracked which means the backend getTags should get the id
    // when autocompleting so the tag color can be used here
    public addGroup(tag: AddTag) {
        const name = tag.name!;
        if (!tag.create) {
            const tagUpdate: TagUpdate = { name: tag.tag!.name, id: tag.tag!.order };
            this.handleAddTagComplete(tagUpdate);
        }
        this.addTag.emit(tag);

        // this.dashboard.updateProject(this.project, true);
    }
    public creatNewTag(name: string, nameIndex: number, groupIndex: number): TagSelection {
        const color = this.colorFactory.getColor(nameIndex);
        return {
            name,
            color: color.color,
            backgroundcolor: color.backgroundcolor,
            isSelected: false,
        };
    }
}
