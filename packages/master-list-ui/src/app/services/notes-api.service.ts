import { Injectable } from '@angular/core';
import { MoveParagraphs, Paragraph } from '../types/note';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '@master-list/environments';
import urlJoin from 'url-join';
import { Observable } from 'rxjs';
import { NoteSaveResult, PageResult, TagProps } from '../types/response/response';

@Injectable({
    providedIn: 'root',
})
export class NotesApiService {
    constructor(private http: HttpClient) {}
    public saveNoteElements(
        items: Paragraph[],
        parent_tag_id: string,
        listType: 'note' | 'tag',
        listName: string,
        page: number | null,
    ): Observable<NoteSaveResult> {
        const parent_list_title = listType === 'note' ? listName : null;
        const body = JSON.stringify({ parent_tag_id, items, parent_list_type: listType, parent_list_title, page });
        const headers = new HttpHeaders().set('Content-Type', 'application/json');
        return this.http.post<NoteSaveResult>(urlJoin(environment.masterListApi, 'note-items'), body, { headers });
    }
    public getNoteElements(noteId: string, listType: 'note' | 'tag', currentPage: number | null): Observable<PageResult> {
        let params = new HttpParams();
        if (currentPage !== null && currentPage !== 0) {
            params = params.set('page', currentPage.toString());
        }
        const page = currentPage !== null && currentPage !== 0 ? currentPage : '';
        return this.http.get<PageResult>(urlJoin(environment.masterListApi, `/note-items/${noteId}/${listType}`), { params });
    }
    public moveNoteElements(
        movedState: MoveParagraphs,
        listId: string,
        listType: 'note' | 'tag',
        tagName: string | null,
        moveType: 'list' | 'page',
        currentPage: number | null,
    ): Observable<NoteSaveResult> {
        const body = JSON.stringify({
            moved_state: movedState,
            list_id: listId,
            list_type: listType,
            tag_name: tagName,
            move_type: moveType,
            current_page: currentPage,
        });
        const headers = new HttpHeaders().set('Content-Type', 'application/json');
        return this.http.post<NoteSaveResult>(urlJoin(environment.masterListApi, 'note-items/move'), body, { headers });
    }
}
