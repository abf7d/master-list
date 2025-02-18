import { Injectable } from '@angular/core';
import { ColorFactoryService } from './color-factory.service';
import { Activity, Project } from '../types/projtect';
// import { TagGroupOption } from '../types/tag/tag-group-option';
import { TagGroup, TagGroupOption, TagSelection, TagSelectionGroup } from '../types/tag';
// import { Activity, Project, TagGroup, TagGroupOption, TagLoad, TagSelection, TagSelectionGroup } from '@critical-pass/project/types';
// import { ColorFactoryService } from '@critical-pass/shared/serializers';

@Injectable({
    providedIn: 'root',
})
export class TagManagerService {
    constructor(private colorFactory: ColorFactoryService) {}

    public addTagGroup(project: Project, name: string, items: string[]) {
        if (!project.tags) {
            project.tags = [];
        }
        items = Array.from(new Set(items));
        const groupIndex = project.tags.length;
        const scheme = this.colorFactory.getSchemeByIndex(0);
        const color = scheme.colors[groupIndex % scheme.colors.length];
        const groupScheme = this.colorFactory.getSchemeByIndex(groupIndex);
        const tags = items.map((x, i) => {
            const itemColor = groupScheme.colors[i % groupScheme.colors.length];
            return {
                name: x,
                color: itemColor.color,
                backgroundcolor: itemColor.backgroundcolor,
            };
        });
        const tagGroup: TagGroupOption = {
            color: color.color,
            backgroundcolor: color.backgroundcolor,
            name,
            tags,
        };
        project.tags.push(tagGroup);
    }

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

    public addNewTagGroup(project: Project, name: string) {
        if (!project.tags) {
            project.tags = [];
        }
        const groupIndex = project.tags.length;
        const scheme = this.colorFactory.getSchemeByIndex(0);
        const color = scheme.colors[groupIndex % scheme.colors.length];
        const tagGroup: TagGroupOption = {
            color: color.color,
            backgroundcolor: color.backgroundcolor,
            name,
            tags: [],
        };
        project.tags.push(tagGroup);
    }
    public createNewTag(project: Project, groupName: string, name: string) {
        // get index of groupName from project.tags
        const groupIndex = project.tags?.findIndex(x => x.name === groupName) ?? 0;
        const groupScheme = this.colorFactory.getSchemeByIndex(groupIndex);
        // get index of tag name from project.tags.tags
        const itemIndex = project.tags?.find(x => x.name === groupName)?.tags?.length ?? 0;

        const tagColor = groupScheme.colors[itemIndex % groupScheme.colors.length];
        const newTag = {
            name,
            color: tagColor.color,
            backgroundcolor: tagColor.backgroundcolor,
        };
        return newTag;
    }

    // Todo In jiraProjectMapper pass the assignee along with one activity
    public addTagToActivities(project: Project, tagName: string, tagGroupName: string, activities: Activity[]) {
        const group = project.tags?.find(x => x.name === tagGroupName);
        if (!group) {
            if (project.tags) {
                this.addNewTagGroup(project, tagGroupName);
                const newTag = this.createNewTag(project, tagGroupName, tagName);
                project.tags.find(x => x.name === tagGroupName)?.tags?.push(newTag);
            }
        }
        activities.forEach(a => {
            //check if group name already exists in activity.tags
            const existingTagGroup = a.tags?.find(x => x.name === tagGroupName);

            //check if tag name exists in groups tags
            const existingTagName = existingTagGroup?.tags?.find(x => x.name === tagName);

            if (existingTagName) {
                return;
            }

            // get tag from project.tags
            const tag = project?.tags?.find(x => x.name === tagGroupName)?.tags.find(x => x.name === tagName);

            // create new activity-tag with project-tag color
            const activityTag = {
                name: tagName,
                color: tag?.color ?? 'black',
                backgroundcolor: tag?.backgroundcolor ?? 'white',
            };

            if (existingTagGroup) {
                existingTagGroup.tags.push(activityTag);
                return;
            }
            const aTagGroup: TagGroup = {
                name: tagGroupName,
                tags: [activityTag],
            };
            a.tags = a.tags ?? [];
            a.tags.push(aTagGroup);
        });
        return;
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

//     private clearLasso(project: Project) {
//         project.profile.view.lassoStart = null;
//         project.profile.view.lassoEnd = null;
//         project.profile.view.lassoedLinks = [];
//         project.profile.view.lassoedNodes = [];
//         project.profile.view.isSubProjSelected = false;
//     }

//     public loadTags(project: Project, tagInfo: TagLoad): void {
//         let tags: TagSelection[] = [];
//         let groups: TagSelectionGroup[] = [];
//         let activeGroup: TagSelectionGroup | null = null;
//         if (project.tags) {
//             tags = project.tags.map(x => ({
//                 name: x.name,
//                 backgroundcolor: x.backgroundcolor,
//                 color: x.color,
//                 isSelected: project.profile.view.selectedTagGroup === x.name,
//             }));
//             groups = project.tags.map(x => ({
//                 name: x.name,
//                 tags: x.tags?.map(y => ({
//                     name: y.name,
//                     color: y.color,
//                     backgroundcolor: y.backgroundcolor,
//                     isSelected: false,
//                 })),
//             }));
//             if (project.profile.view.selectedTagGroup) {
//                 activeGroup = groups.find(x => x.name === project.profile.view.selectedTagGroup) ?? null;
//             }
//         }
//         tagInfo.tags = tags;
//         tagInfo.groups = groups;
//         tagInfo.activeGroup = activeGroup;
//     }
// }
}
