import { Inject, Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { from, Observable, of, switchMap } from 'rxjs';
import { JwtHelperService } from '@auth0/angular-jwt';
import * as CONST from '../constants';
import { MSAL_GUARD_CONFIG, MsalBroadcastService, MsalGuard, MsalGuardConfiguration, MsalService } from '@azure/msal-angular';
import { Location } from '@angular/common';
import { AuthCoreService } from '../auth-service/auth.service';
import { ClaimsService } from '../claims-service/claims.service';

@Injectable({
    providedIn: 'root',
})
export class AuthorizedUserGuard extends MsalGuard implements CanActivate {
    jwtHelper: JwtHelperService;
    parentRouter!: Router;
    msalService!: MsalService;
    constructor(
        private authCoreService: AuthCoreService,
        private accountData: ClaimsService,
        msalBroadcastService: MsalBroadcastService,
        authService: MsalService,
        location: Location,
        parentRouter: Router,
        @Inject(MSAL_GUARD_CONFIG) private guardConfig: MsalGuardConfiguration,
    ) {
        super(guardConfig, msalBroadcastService, authService, location, parentRouter);
        this.parentRouter = parentRouter;
        this.msalService = authService;
        this.jwtHelper = new JwtHelperService();
    }

    override canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean | UrlTree> {
        return super.canActivate(route, state).pipe(
            switchMap((msalResult: boolean | UrlTree) => {
                // If MSAL guard returned a UrlTree (redirect), use it
                if (msalResult instanceof UrlTree) {
                    return of(msalResult);
                }
                // If MSAL guard fails, it will handle redirect automatically
                if (!msalResult) {
                    return of(false);
                }
                // If MSAL authentication passed, check our custom token and claims
                return from(this.checkTokenAndClaims(state));
            }),
        );
    }

    private async checkTokenAndClaims(state: RouterStateSnapshot): Promise<boolean | UrlTree> {
        try {
            // First get the token - this ensures we're authenticated
            const token = await this.authCoreService.getAuthToken();

            // Check if token is expired
            const isLoggedIn = !this.authCoreService.accessExpired();

            // TODO: Token expired, clear claims and redirect to login
            if (!isLoggedIn) {
                // this.accountData.clearClaims();
                // sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
                // this.authCoreService.login();
                // return false;
            }

            // Check if claims are already loaded
            if (!this.accountData.isExpired()) {
                // Claims already exist, check authorization
                const isAuthorized = this.accountData.isAdmin() || this.accountData.isAuthorized();
                if (!isAuthorized) {
                    console.error('unexpired but unauthorized in auth-user-gaurd');
                    // User is authenticated but not authorized
                    return this.parentRouter.createUrlTree(['/unauthorized']);
                }
                console.log('cached is Authorized to view pages');
                return true;
            }

            // Claims not loaded yet, force loading them
            try {
                // This will load claims from backend and should return whether user is authorized
                const isAuthorized = await this.accountData.initializeClaims();
                if (!isAuthorized) {
                    console.error('fresh retreival unauthorized in auth-user-gaurd');
                    return this.parentRouter.createUrlTree(['/unauthorized']);
                }
                console.log('api call is Authorized to view pages');
                return true;
            } catch (claimsError: any) {
                console.error('Failed to load claims:', claimsError);
                if (claimsError.status === 401) {
                    this.accountData.clearClaims();
                    this.authCoreService.login();
                    return false;
                }
                return this.parentRouter.createUrlTree(['/error']);
            }
        } catch (error: any) {
            this.accountData.clearClaims();

            if (error.errorCode === 'no_account_error') {
                sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
                this.authCoreService.login();
                return false;
            }

            return this.parentRouter.createUrlTree(['/home']);
        }
    }
}
