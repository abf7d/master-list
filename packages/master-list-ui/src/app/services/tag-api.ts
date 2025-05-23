import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '@master-list/environments';
import urlJoin from 'url-join';
import { TagButton, TagSelection, TagSelectionGroup } from '../types/tag';
import { Observable, of } from 'rxjs';
import { TagUpdate } from '../types/tag/tag-update';
import { NoteSerach, TagCreate, TagSearch, Response } from '../types/response/response';



@Injectable({
    providedIn: 'root',
})
export class TagApiService {
    constructor(private http: HttpClient) {}
    // API calls for notes

    public getTagsOld(size: number, page: number, isList: boolean = false): Observable<any> {
        let params = new HttpParams().set('size', size.toString()).set('page', page.toString()).set('islist', page.toString());
        return this.http.get(urlJoin(environment.masterListApi, '/tags'), { params });
    }

    public getTags(searchTxt: string | null, page: number, pageSize: number, id: string | null = null): Observable<TagSearch> {
        let params = new HttpParams().set('query', searchTxt ?? '').set('page', page.toString()).set('pageSize', pageSize.toString())
        params = (id !== null) ? params.set('id', id) : params;
        return this.http.get<TagSearch>(urlJoin(environment.masterListApi, '/tags'), { params });
    }
    public getNotes(searchTxt: string | null, page: number, pageSize: number, id: string | null = null): Observable<NoteSerach> {
        let params = new HttpParams().set('query', searchTxt ?? '').set('page', page.toString()).set('pageSize', pageSize.toString());
        params = (id !== null) ? params.set('id', id) : params;
        return this.http.get<NoteSerach>(urlJoin(environment.masterListApi, '/notes'), { params });
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

    public createNote(type: string): Observable<TagCreate> {
        let params = new HttpParams().set('type', type)
       return  this.http.post<TagCreate>(urlJoin(environment.masterListApi, '/note'), { params });

    }
    public deleteNote(id: string): Observable<Response<any>> {
        return this.http.delete<Response<any>>(urlJoin(environment.masterListApi, '/note', id));
    }

    public getDefaultTags(): Observable<TagSelectionGroup> {
        return of({
            name: 'Tag Group',
            tags: [
                {
                    name: 'Critical Pass',
                    color: 'white',
                    backgroundcolor: '#e6194b',
                    isSelected: false,
                },
                {
                    name: 'Work',
                    color: 'white',
                    backgroundcolor: '#3cb44b',
                    isSelected: false,
                },
                {
                    name: 'Misc Triage',
                    color: 'black',
                    backgroundcolor: '#ffe119',
                    isSelected: false,
                },
            ],
        });
    }
}
