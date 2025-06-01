import { TagProps } from "../response/response";
import { TagSelection } from "./tag";

export interface AddTag {
    name?: string;
    tag?: TagProps;
    create: boolean;
}
export interface RemoveTag {
    tag?: TagSelection;
    delete: boolean;
}
export interface MoveItems {
    action: 'move' | 'archive';
    tagName: string;
}