import { TagEntry, TagGroup, TagGroupOption } from "./tag";

export interface Project {
    id: string;
    name: string;
    description: string;
    tags: TagGroupOption[];
    activities: Activity[];
    profile: ProjectProfile;
}
export interface ProjectProfile {
    view: ProjectView;
}
export interface ProjectView {
    selectedTagGroup: string | null;
}
export interface Activity {
    id: string;
    tags?: TagGroup[];
    content: string;
}
    