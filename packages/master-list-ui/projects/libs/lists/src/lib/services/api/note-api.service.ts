import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '@env/environment';
import urlJoin from 'url-join';
import { Observable } from 'rxjs';
import { NoteSerach, TagCreate } from '../../types/response/response';

import { Response } from '../../types/response/response';
@Injectable({
    providedIn: 'root',
})
export class NoteApiService {
    constructor(private http: HttpClient) {}

    public getNotes(searchTxt: string | null, page: number, pageSize: number, id: string | null = null): Observable<NoteSerach> {
        let params = new HttpParams()
            .set('query', searchTxt ?? '')
            .set('page', page.toString())
            .set('pageSize', pageSize.toString());
        params = id !== null ? params.set('id', id) : params;
        return this.http.get<NoteSerach>(urlJoin(environment.masterListApi, '/notes'), { params });
    }
    public createNote(type: string): Observable<TagCreate> {
        let params = new HttpParams().set('type', type);
        return this.http.post<TagCreate>(urlJoin(environment.masterListApi, '/note'), { params });
    }
    public deleteNote(id: string): Observable<Response<any>> {
        return this.http.delete<Response<any>>(urlJoin(environment.masterListApi, '/note', id));
    }
}
