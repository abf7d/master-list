import { Injectable } from "@angular/core";
import { Paragraph } from "../types/note";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { environment } from "@master-list/environments";
import urlJoin from "url-join";
import { Observable } from "rxjs";
import { NoteSaveResult, PageResult, TagProps } from "../types/response/response";

@Injectable({
    providedIn: 'root',
})
export class NotesApiService {
    constructor(private http: HttpClient) {}
    public saveNoteElements(items: Paragraph[], parent_tag_id: string, listType: 'note' | 'tag', listName: string ): Observable<NoteSaveResult> {
        const parent_list_title =  listType === 'note' ? listName : null;
        const body = JSON.stringify({parent_tag_id, items, parent_list_type:listType, parent_list_title});
        const headers = new HttpHeaders().set('Content-Type', 'application/json');
        return this.http.post<NoteSaveResult>(urlJoin(environment.masterListApi, 'note-items'),  body, { headers });
    }
    // API calls for notes
    public getNoteElements(noteId: string, listType: 'note' | 'tag'): Observable<PageResult> {
        // Call the API to get elements for a note
        return this.http.get<PageResult>(urlJoin(environment.masterListApi, `/note-items/${noteId}/${listType}`));
      
    }
}
