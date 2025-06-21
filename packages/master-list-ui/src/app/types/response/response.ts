import { Paragraph } from "../note";

export interface Response<T> {
    message: string;
    error?: string;
    data: T;
}

export interface TagProps {
    id: string;
    name: string;
    parent_id: string;
    created_at: string;
    order: number;
    max_page?: number | null;
    page?: number | null;
}
export interface NoteProps {
    id: string;
    title: string;
    description: string;
    create_at: string;
    updated_at: string;
    order: number;
    max_page: number | null;
}
export interface TagSearch extends Response<TagProps[]> {}
export interface TagCreate extends Response<TagProps> {}
export interface NoteSerach extends Response<NoteProps[]>{}

export interface NoteSaveResult {
    message:string;
    data:any;
}

export interface PageResult {
    message: string;
    error?: string;
    data: NoteElementResponse;
}
export interface NoteElementResponse {
    notes: Paragraph[];
    tags: TagProps[];
    list_name: string;
    list_type: string;
    color_order: number | null;
    max_page: number;
}