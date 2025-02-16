import { Injectable } from '@angular/core';
// import { TagGroup, TagGroupOption, TagLoad, TagSelection, TagSelectionGroup } from '../../types/tag';
import { Project } from '../../types/projtect';
import { TagGroupOption, TagLoad, TagSelection, TagSelectionGroup } from '../../types/tag';

@Injectable({
    providedIn: 'root',
})
export class MetaTagService {
    public addTagGroupToProject(project: Project, tagGroup: TagGroupOption) {
        project.tags = project.tags ?? [];
        project.tags = project.tags.filter(x => x.name !== tagGroup.name);
        project.tags.push({
            name: tagGroup.name,
            tags: tagGroup.tags.map(t => {
                return {
                    name: t.name,
                    color: t.color,
                    backgroundcolor: t.backgroundcolor,
                };
            }),
            color: tagGroup.color,
            backgroundcolor: tagGroup.backgroundcolor,
        });
    }
    public removeTagFromActivities(project: Project, groupName: string, tag: TagSelection) {
        project.activities.forEach(a => {
            if (a.tags) {
                const group = a.tags.find(x => x.name === groupName);
                if (group) {
                    group.tags = group.tags.filter(x => x.name !== tag.name);
                }
            }
        });
    }
    public removeTagGroupFromProject(project: Project, tag: TagSelection) {
        if (!project.tags) {
            return;
        }
        project.tags = project.tags.filter(x => x.name !== tag.name);
        project.activities.forEach(a => {
            a.tags = a.tags ?? [];
            a.tags = a.tags.filter(x => x.name !== tag.name);
        });
        if (project.profile.view.selectedTagGroup === tag.name) {
            project.profile.view.selectedTagGroup = null;
        }
        project.tags = project.tags?.filter(x => x.name !== tag.name);
    }
    public assignTagsToSelectedActivities(project: Project, tagNames: string[], tagGroup: TagSelectionGroup): void {
        // const selectedLinkids = project.profile.view?.lassoedLinks;
        // const tags = tagGroup.tags.filter(x => tagNames.indexOf(x.name) > -1);
        // if (selectedLinkids?.length > 0) {
        //     const activities = project.activities.filter(x => selectedLinkids.indexOf(x.profile.id) > -1);
        //     activities.forEach(a => {
        //         const aTagGroup: TagGroup = {
        //             name: tagGroup.name,
        //             tags: tags.map(t => {
        //                 return {
        //                     name: t.name,
        //                     color: t.color,
        //                     backgroundcolor: t.backgroundcolor,
        //                 };
        //             }),
        //         };
        //         a.tags = a.tags ?? [];
        //         a.tags = a.tags.filter(x => x.name !== tagGroup.name);
        //         a.tags.push(aTagGroup);
        //     });
        // }
        // this.clearLasso(project);
    }

    public unassignFromActivities(group: string, project: Project): void {
        // const selectedLinkids = project.profile.view?.lassoedLinks;
        // if (selectedLinkids?.length > 0) {
        //     const activities = project.activities.filter(x => selectedLinkids.indexOf(x.profile.id) > -1);
        //     activities.forEach(a => {
        //         if (a.tags) {
        //             a.tags = a.tags.filter(x => x.name != group);
        //         }
        //     });
        // }
        // this.clearLasso(project);
    }

    // private clearLasso(project: Project) {
    //     project.profile.view.lassoStart = null;
    //     project.profile.view.lassoEnd = null;
    //     project.profile.view.lassoedLinks = [];
    //     project.profile.view.lassoedNodes = [];
    //     project.profile.view.isSubProjSelected = false;
    // }

    public loadTags(project: Project, tagInfo: TagLoad): void {
        let tags: TagSelection[] = [];
        let groups: TagSelectionGroup[] = [];
        let activeGroup: TagSelectionGroup | null = null;
        if (project.tags) {
            tags = project.tags.map(x => ({
                name: x.name,
                backgroundcolor: x.backgroundcolor,
                color: x.color,
                isSelected: project.profile.view.selectedTagGroup === x.name,
            }));
            groups = project.tags.map(x => ({
                name: x.name,
                tags: x.tags?.map(y => ({
                    name: y.name,
                    color: y.color,
                    backgroundcolor: y.backgroundcolor,
                    isSelected: false,
                })),
            }));
            if (project.profile.view.selectedTagGroup) {
                activeGroup = groups.find(x => x.name === project.profile.view.selectedTagGroup) ?? null;
            }
        }
        tagInfo.tags = tags;
        tagInfo.groups = groups;
        tagInfo.activeGroup = activeGroup;
    }
}
