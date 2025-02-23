import { BehaviorSubject } from 'rxjs';
import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class AuthStateService {
    public isLoggedIn$: BehaviorSubject<boolean | null>;
    public loginError$: BehaviorSubject<boolean | null>;
    public isAuthorized$: BehaviorSubject<boolean | null>;
    public redirectUrl: string | null = null;

    constructor() {
        this.isLoggedIn$ = new BehaviorSubject<boolean | null>(null);
        this.loginError$ = new BehaviorSubject<boolean | null>(null);
        this.isAuthorized$ = new BehaviorSubject<boolean | null>(null);
    }
}
