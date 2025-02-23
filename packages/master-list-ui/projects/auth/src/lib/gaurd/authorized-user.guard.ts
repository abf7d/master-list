import { Injectable } from '@angular/core';
import { Router, CanLoad, Route, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';
import { JwtHelperService } from '@auth0/angular-jwt';
import { ClaimsService, MsalService } from '@master-list/auth';
import { environment } from '@master-list/environments';
import * as CONST from '../constants';

@Injectable({
    providedIn: 'root',
})
export class AuthorizedUserGuard implements CanActivate {
    jwtHelper: JwtHelperService;
    constructor(
        private authService: MsalService,
        private accountData: ClaimsService,
        private router: Router,
    ) {
        this.jwtHelper = new JwtHelperService();
    }

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Promise<boolean> {
        return this.authService
            .getAuthToken()
            .then(token => {
                const isLoggedIn = !this.authService.accessExpired();
                if (!isLoggedIn) {
                    // claims need to include user id in name so the someone else's claims can't be reused
                    this.accountData.clearClaims();
                    sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
                    this.authService.login();
                    return false;
                }
                // Check if token has expired, if so, return false
                return this.accountData.isAdmin() || this.accountData.isAuthorized();
            })
            .catch(error => {
                this.accountData.clearClaims();
                if (error.errorCode === 'no_account_error') {
                    sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
                    this.authService.login();
                    return false;
                }
                this.router.navigate(['/home']);
                return false;
            });
    }
}
