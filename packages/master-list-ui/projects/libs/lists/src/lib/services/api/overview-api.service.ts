import { Injectable } from '@angular/core';
import { MoveParagraphs, Paragraph } from '../../../../../../libs/lists/src/lib/types/note';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '@env/environment';
import urlJoin from 'url-join';
import { Observable } from 'rxjs';
import { NoteSaveResult, NoteSerach, PageResult, TagCreate, TagProps } from '../../../../../../libs/lists/src/lib/types/response/response';

@Injectable({
    providedIn: 'root',
})
export class OverviewApiService {
    constructor(private http: HttpClient) {}
    /**
     * Fetches the overview of a note or tag.
     * @param noteId The ID of the note or tag.
     * @param listType The type of list, either 'note' or 'tag'.
     * @param currentPage The current page number, or null for the first page.
     * @returns An observable containing the page result.
     */
    public getOverview(noteId: string, listType: 'note' | 'tag', currentPage: number | null): Observable<PageResult> {
        let params = new HttpParams();
        if (currentPage !== null && currentPage !== 0) {
            params = params.set('page', currentPage.toString());
        }
        const page = currentPage !== null && currentPage !== 0 ? currentPage : '';
        return this.http.get<PageResult>(urlJoin(environment.masterListApi, `/${listType}/${noteId}/overview`), { params });
    }

}
