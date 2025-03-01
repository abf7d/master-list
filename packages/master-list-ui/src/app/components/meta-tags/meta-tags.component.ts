import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TagButton, TagGroupOption, TagSelection, TagSelectionGroup } from '../../types/tag';
import { ColorFactoryService } from '../../services/color-factory.service';
import { TagManagerService } from '../../services/tag-manager.service';
import { Project } from '../../types/projtect';
import { CommonModule } from '@angular/common';
import { TagGroupComponent } from '../tag-group/tag-group.component';

@Component({
  selector: 'app-meta-tags',
  imports: [CommonModule, TagGroupComponent],
  templateUrl: './meta-tags.component.html',
  styleUrl: './meta-tags.component.scss',
})
export class MetaTagsComponent {
  @Output() assignTag = new EventEmitter<string>();
  @Output() unAssignTag = new EventEmitter<string>();
  @Input() tags: TagButton[] = [];

  @Input() allowAdd = true;
  public tagGroups: TagSelectionGroup;
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
    private metaTagService: TagManagerService
  ) {
    // this.id = +route.snapshot.params['id'];
    // this.project$ = this.dashboard.activeProject$;
    // const focusTag = this.creatNewTag('Focus', 0, 0); // high priority
    // const backgroundTag = this.creatNewTag('Background', 1, 0); // low prioritiy
    // const storageTag = this.creatNewTag('Storage', 2, 0);
    // const deleteTag = this.creatNewTag('Delete', 3, 0);
    this.tagGroups = { name: 'Tag Group', tags: [] };
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
    this.addGroup('Critical Pass');
    this.addGroup('Work')
    this.addGroup('Misc Triage');
    // this.addGroup('Focus');
    // this.addGroup('Background');
    // this.addGroup('Storage');
    // this.addGroup('Delete');
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
      const activeGroup = this.availableGroups.find((x) => x.name === name);
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
  public assignGroup(name: string[]){
    this.assignTag.emit(name[0]);
  }
  public removeGroup(tag: TagSelection) {
    this.tagGroups.tags.splice(this.tagGroups.tags.indexOf(tag), 1);
    const groupIndex = this.availableGroups.findIndex(
      (x) => x.name === tag.name
    );

    if (groupIndex > -1) {
      this.metaTagService.removeTagGroupFromProject(this.project, tag);
      this.availableGroups.splice(groupIndex, 1);
    }
    // this.dashboard.updateProject(this.project, true);
   
  }
  public addGroup(name: any) {
    const newTag = this.creatNewTag(name, this.tagGroups.tags.length, 0);
    this.tagGroups.tags.push(newTag);

    const newSelectionGroup: TagSelectionGroup = { name, tags: [] };
    this.availableGroups.push(newSelectionGroup);

    const newTagGroupOption: TagGroupOption = {
      name,
      tags: [],
      color: newTag.color,
      backgroundcolor: newTag.backgroundcolor,
    };
    this.metaTagService.addTagGroupToProject(this.project, newTagGroupOption);
    // this.dashboard.updateProject(this.project, true);
  }
  public creatNewTag(
    name: string,
    nameIndex: number,
    groupIndex: number
  ): TagSelection {
    const scheme = this.colorFactory.getSchemeByIndex(groupIndex);
    const color = scheme.colors[nameIndex % scheme.colors.length];
    return {
      name,
      color: color.color,
      backgroundcolor: color.backgroundcolor,
      isSelected: false,
    };
  }
}
