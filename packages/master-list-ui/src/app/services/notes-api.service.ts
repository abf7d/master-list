import { Injectable } from "@angular/core";
import { NoteElement, Paragraph } from "../types/note";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { environment } from "@master-list/environments";
import urlJoin from "url-join";
import { Observable } from "rxjs";

@Injectable({
    providedIn: 'root',
})
export class NotesApiService {
    constructor(private http: HttpClient) {}
    public saveNoteElements(items: Paragraph[], parentNoteId: string ): Observable<NoteSaveResult> {
        const body = JSON.stringify({parentNoteId, items});
        const headers = new HttpHeaders().set('Content-Type', 'application/json');
        return this.http.post<NoteSaveResult>(urlJoin(environment.masterListApi, 'note-items'),  body, { headers });
    }
    // API calls for notes
    getNoteElements(noteId: string): Observable<NoteElement[]> {
        // Call the API to get elements for a note
        return this.http.get<NoteElement[]>(urlJoin(environment.masterListApi, `/note-items/${noteId}`));
      
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
export interface NoteSaveResult {
    message:string;
    data:any;
}