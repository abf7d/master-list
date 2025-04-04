import { Injectable } from '@angular/core';
import { NoteElement } from '../types/note';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { environment } from '@master-list/environments';
import urlJoin from 'url-join';
import { TagButton, TagSelection, TagSelectionGroup } from '../types/tag';
import { Observable, of } from 'rxjs';
import { TagUpdate } from '../types/tag/tag-update';

export interface Response<T> {
    message: string;
    error?: string;
    data: T;
}

export interface TagProps {
    id: string;
    name: string;
    parent_id: string;
    created_at: string;
    order: number;

}
export interface TagSerch extends Response<TagProps[]>{

}
export interface TagCreate extends Response<TagProps>{
}

@Injectable({
    providedIn: 'root',
})
export class TagApiService {
    constructor(private http: HttpClient) {}
    // API calls for notes


    public getTags(size: number, page: number, isList: boolean = false): Observable<any> {
        let params = new HttpParams()
            .set('size', size.toString())
            .set('page', page.toString())
            .set('islist', page.toString());
        return this.http.get(urlJoin(environment.masterListApi, '/tags'), { params });
    }

    autoCompleteTags(searchTxt: string, page: number, pageSize: number): Observable<TagSerch>  {
        let params = new HttpParams().set('query', searchTxt).set('page', page.toString()).set('pageSize', pageSize.toString());
        return this.http.get<TagSerch>(urlJoin(environment.masterListApi, '/tags'), { params });
    }

    // public createTag(tag: TagButton): Observable<any>{
    //     const body = JSON.stringify(tag);
    //     const headers = new HttpHeaders().set('Content-Type', 'application/json');

    //     return this.http
    //         .post<Response<any>>(urlJoin(environment.masterListApi, '/tag'), body, { headers });
    // }

    public createTag(tag: string): Observable<TagCreate> {
        const body = JSON.stringify({ name: tag });
        const headers = new HttpHeaders().set('Content-Type', 'application/json');

        return this.http.post<TagCreate>(urlJoin(environment.masterListApi, '/tag'), body, { headers });
    }

    public deleteTag(name: string): Observable<any> {
        const nameEncoded = encodeURIComponent(name);
        return this.http.delete<Response<any>>(urlJoin(environment.masterListApi, '/tag', nameEncoded));
    }

    public getLists(): Observable<TagSelectionGroup> {
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

