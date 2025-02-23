import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import urlJoin from 'url-join';
import { environment } from '@master-list/environments';
@Injectable({
    providedIn: 'root',
})
export class ClaimsApiService {
    constructor(private http: HttpClient) {}

    public getClaims(): Observable<any> {
        return this.http.get(urlJoin(environment.masterListApi, '/account/get-token?token_type=claims'));
    }
}
