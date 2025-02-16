export interface Tag {
    name: string;
    color: string;
    backgroundcolor: string;
}
export interface TagButton {
    name: string;
    color: string;
    backgroundcolor: string;
}
export interface TagSelectionGroup {
    name: string;
    tags: TagSelection[];
}
export interface TagLoad {
    tags: TagSelection[];
    groups: TagSelectionGroup[];
    activeGroup: TagSelectionGroup | null;
}
export interface TagSelection extends TagButton {
    isSelected: boolean;
}
export interface TagGroupOption {
    color: string;
    backgroundcolor: string;
    name: string;
    tags: TagButton[];
}
export interface TagEntry {
    group: string;
    activityId: number;
    graphId: number;
    nodeId: number;
}
export interface TagGroup {
    name: string;
    tags: Tag[];
}
