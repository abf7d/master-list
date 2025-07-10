import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '@env/environment';
import urlJoin from 'url-join';
import { Observable } from 'rxjs';
import { TagCreate, TagSearch, Response } from '../../types/response/response';

@Injectable({
    providedIn: 'root',
})
export class TagApiService {
    constructor(private http: HttpClient) {}

    public getTags(searchTxt: string | null, page: number, pageSize: number, id: string | null = null): Observable<TagSearch> {
        let params = new HttpParams()
            .set('query', searchTxt ?? '')
            .set('page', page.toString())
            .set('pageSize', pageSize.toString());
        params = id !== null ? params.set('id', id) : params;
        return this.http.get<TagSearch>(urlJoin(environment.masterListApi, '/tags'), { params });
    }

    public createTag(tag: string): Observable<TagCreate> {
        const body = JSON.stringify({ name: tag });
        const headers = new HttpHeaders().set('Content-Type', 'application/json');

        return this.http.post<TagCreate>(urlJoin(environment.masterListApi, '/tag'), body, { headers });
    }

    public deleteTag(name: string): Observable<any> {
        const nameEncoded = encodeURIComponent(name);
        return this.http.delete<Response<any>>(urlJoin(environment.masterListApi, '/tag', nameEncoded));
    }

}
