import { Injectable } from "@angular/core";
import { NoteElement } from "../types/note";
import { HttpClient } from "@angular/common/http";
import { environment } from '@master-list/environments';
import urlJoin from "url-join";

@Injectable({
    providedIn: 'root',
})
export class TagApiService {
    constructor(private http: HttpClient) {}
    // API calls for notes
    async getTags(noteId: string): Promise<NoteElement[]> {
        // Call the API to get elements for a note
        this.http.get(urlJoin(environment.masterListApi, '/account/get-token?token_type=claims'));
        return [];
    }
    
    async updateNoteElements(noteId: string, elements: NoteElement[]): Promise<void> {
        // Call the API to update elements for a note
    }
    
    async createNoteElement(noteId: string, element: NoteElement): Promise<void> {
        // Call the API to create a new element
    }
    
    async deleteNoteElement(noteId: string, elementId: string): Promise<void> {
        // Call the API to delete an element
    }
}