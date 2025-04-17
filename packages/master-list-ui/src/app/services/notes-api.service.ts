import { Injectable } from "@angular/core";
import { NoteElement, Paragraph } from "../types/note";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { environment } from "@master-list/environments";
import urlJoin from "url-join";
import { Observable } from "rxjs";
import { TagUpdate } from "../types/tag/tag-update";
import { TagProps } from "./tag-api";

@Injectable({
    providedIn: 'root',
})
export class NotesApiService {
    constructor(private http: HttpClient) {}
    public saveNoteElements(items: Paragraph[], parent_tag_id: string ): Observable<NoteSaveResult> {
        const body = JSON.stringify({parent_tag_id, items});
        const headers = new HttpHeaders().set('Content-Type', 'application/json');
        return this.http.post<NoteSaveResult>(urlJoin(environment.masterListApi, 'note-items'),  body, { headers });
    }
    // API calls for notes
    public getNoteElements(noteId: string, listType: 'note' | 'tag'): Observable<PageResult> {
        // Call the API to get elements for a note
        return this.http.get<PageResult>(urlJoin(environment.masterListApi, `/note-items/${noteId}/${listType}`));
      
    }
    
    // async updateNoteElements(noteId: string, elements: NoteElement[]): Promise<void> {
    //     // Call the API to update elements for a note
    // }
    
    // async createNoteElement(noteId: string, element: NoteElement): Promise<void> {
    //     // Call the API to create a new element
    // }
    
    // async deleteNoteElement(noteId: string, elementId: string): Promise<void> {
    //     // Call the API to delete an element
    // }


}
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
}