import { Inject, Injectable } from '@angular/core';
import { Router, CanLoad, Route, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { catchError, from, map, Observable, of, switchMap } from 'rxjs';
import { JwtHelperService } from '@auth0/angular-jwt';
import { AuthCoreService, ClaimsService /*MsalService*/ } from '@master-list/auth';
import { environment } from '@master-list/environments';
import * as CONST from '../constants';
import { MSAL_GUARD_CONFIG, MsalBroadcastService, MsalGuard, MsalGuardConfiguration, MsalService } from '@azure/msal-angular';
import { InteractionType } from '@azure/msal-browser';
import { Location } from '@angular/common';

@Injectable({
    providedIn: 'root',
})
export class AuthorizedUserGuard extends MsalGuard implements CanActivate {
    jwtHelper: JwtHelperService;
    parentRouter!: Router;
    msalService!: MsalService;
    constructor(
        private authCoreService: AuthCoreService,
        // private msalService: MsalService,
        private accountData: ClaimsService,
        // private routerTop: Router,
       
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


    
    
        // override canActivate(
        //     route: ActivatedRouteSnapshot, 
        //     state: RouterStateSnapshot
        // ): Observable<boolean | UrlTree> {
        //     // First check if we have an active account
        //     const account = this.msalService.instance.getActiveAccount();
            
        //     if (account) {
        //         // Check if the token is expired
        //         const isTokenExpired = this.isTokenExpired();
                
        //         if (isTokenExpired) {
        //             // If token is expired, try to renew it silently before proceeding
        //             return this.renewTokenSilently().pipe(
        //                 switchMap(renewSuccess => {
        //                     if (renewSuccess) {
        //                         // Continue with the original guard logic after token renewal
        //                         return this.proceedWithGuardChecks(route, state);
        //                     } else {
        //                         this.authCoreService.login();
        //                         // If renewal failed, redirect to login
        //                         return of(false);
        //                     }
        //                 })
        //             );
        //         }
        //     }
            
        //     // If no account or token is not expired, proceed with regular checks
        //     return this.proceedWithGuardChecks(route, state);
        // }
        
        // private proceedWithGuardChecks(
        //     route: ActivatedRouteSnapshot, 
        //     state: RouterStateSnapshot
        // ): Observable<boolean | UrlTree> {
        //     // Original guard logic
        //     return super.canActivate(route, state).pipe(
        //         switchMap((msalResult: boolean | UrlTree) => {
        //             // If MSAL guard returned a UrlTree (redirect), use it
        //             if (msalResult instanceof UrlTree) {
        //                 return of(msalResult);
        //             }
        //             // If MSAL guard fails, it will handle redirect automatically
        //             if (!msalResult) {
        //                 return of(false);
        //             }
                    
        //             // If MSAL authentication passed, check our custom token and claims
        //             return from(this.checkTokenAndClaims(state));
        //         }),
        //         catchError(error => {
        //             console.error('Auth guard error:', error);
        //             return of(this.parentRouter.createUrlTree(['/home']));
        //         })
        //     );
        // }
        
        // private isTokenExpired(): boolean {
        //     try {
        //         const accounts = this.msalService.instance.getAllAccounts();
        //         if (accounts.length === 0) return true;
                
        //         // Get the ID token claims
        //         const account = accounts[0];
        //         const idTokenClaims = account.idTokenClaims as any;
                
        //         if (!idTokenClaims) return true;
                
        //         // Check if token is expired
        //         const expiresOn = idTokenClaims.exp * 1000; // Convert to milliseconds
        //         const now = Date.now();
                
        //         // Consider token expired if it's within 5 minutes of expiration
        //         // This gives us a buffer to renew before actual expiration
        //         return now > (expiresOn - 5 * 60 * 1000);
        //     } catch (error) {
        //         console.error('Error checking token expiration:', error);
        //         return true; // If we can't check, assume it's expired to be safe
        //     }
        // }
        
        // private renewTokenSilently(): Observable<boolean> {
        //     // Get the appropriate scopes from your config
        //     // const scopes = this.guardConfig.authRequest?.scopes || ['user.read'];
            
        //     // return from(this.authService.acquireTokenSilent({ scopes })).pipe(
        //         return from(this.authCoreService.acquireSilent()).pipe(

        //         map(response => {
        //             // Token successfully acquired
        //             return true;
        //         }),
        //         catchError(error => {
        //             console.error('Silent token renewal failed:', error);
                    
        //             // For certain errors, we might want to try interactive auth
        //             if (error.name === 'InteractionRequiredAuthError') {
        //                 // Don't do popup here as we're in a guard - let the redirect happen
        //                 return of(false);
        //             }
                    
        //             return of(false);
        //         })
        //     );
        // }



        // private async checkTokenAndClaims(state: RouterStateSnapshot): Promise<boolean | UrlTree> {
        //         try {
        //             // First get the token - this ensures we're authenticated
        //             const token = await this.authCoreService.getAuthToken();
        
        //             // Check if token is expired
        //             const isLoggedIn = !this.authCoreService.accessExpired();
        //             if (!isLoggedIn) {
        //                 // // Token expired, clear claims and redirect to login
        //                 // this.accountData.clearClaims();
        //                 // sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
        //                 // this.authCoreService.login();
        //                 // return false;
        //             }
        
        //             // Check if claims are already loaded
        //             if (this.accountData.hasClaims()) {
        //                 // Claims already exist, check authorization
        //                 const isAuthorized = this.accountData.isAdmin() || this.accountData.isAuthorized();
        //                 if (!isAuthorized) {
        //                     // User is authenticated but not authorized
        //                     return this.parentRouter.createUrlTree(['/unauthorized']);
        //                 }
        //                 console.log('cached is Authorized to view pages');
        //                 return true;
        //             }
        
        //             // Claims not loaded yet, force loading them
        //             try {
        //                 // This will load claims from backend and should return whether user is authorized
        //                 const isAuthorized = await this.accountData.initializeClaims();
        //                 if (!isAuthorized) {
        //                     return this.parentRouter.createUrlTree(['/unauthorized']);
        //                 }
        //                 console.log('api call is Authorized to view pages');
        //                 return true;
        //             } catch (claimsError: any) {
        //                 console.error('Failed to load claims:', claimsError);
        //                 if (claimsError.status === 401) {
        //                     this.accountData.clearClaims();
        //                     this.authCoreService.login();
        //                     return false;
        //                 }
        //                 return this.parentRouter.createUrlTree(['/error']);
        //             }
        //         } catch (error: any) {
        //             this.accountData.clearClaims();
        
        //             if (error.errorCode === 'no_account_error') {
        //                 sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
        //                 this.authCoreService.login();
        //                 return false;
        //             }
        
        //             return this.parentRouter.createUrlTree(['/home']);
        //         }
        //     }

    override canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean | UrlTree> {
        
        // TODO: When redirect fails again doesn't work try to acquireSilent before calling can activate. The catchError Isn't working
        // here
        
        // First check if the user is authenticated with MSAL

        // TODO: Try to return  just the msalResult to see if the claims stuff is killing the redirect
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
            if (!isLoggedIn) {
                // // Token expired, clear claims and redirect to login
                // this.accountData.clearClaims();
                // sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
                // this.authCoreService.login();
                // return false;
            }

            // Check if claims are already loaded
            if (this.accountData.hasClaims()) {
                // Claims already exist, check authorization
                const isAuthorized = this.accountData.isAdmin() || this.accountData.isAuthorized();
                if (!isAuthorized) {
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
