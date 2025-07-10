import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '@env/environment';
import urlJoin from 'url-join';
import { Observable } from 'rxjs';
import { NoteSaveResult, PageResult } from '../../types/response/response';

@Injectable({
    providedIn: 'root',
})
export class PageApiService {
    constructor(private http: HttpClient) {}
    public deletePage(
        listId: string,
        listType: 'note' | 'tag',
        currentPage: number | null,
    ): Observable<NoteSaveResult> {
        let params = new HttpParams();
        if (currentPage !== null && currentPage !== 0) {
            params = params.set('page', currentPage.toString());
        }
        return this.http.delete<PageResult>(urlJoin(environment.masterListApi, `/${listType}/${listId}/page`), { params });
    }
}



