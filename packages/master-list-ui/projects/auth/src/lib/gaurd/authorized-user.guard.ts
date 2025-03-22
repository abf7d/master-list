import { Inject, Injectable } from '@angular/core';
import { Router, CanLoad, Route, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree, } from '@angular/router';
import { catchError, from, Observable, of, switchMap } from 'rxjs';
import { JwtHelperService } from '@auth0/angular-jwt';
import { AuthCoreService, ClaimsService, /*MsalService*/ } from '@master-list/auth';
import { environment } from '@master-list/environments';
import * as CONST from '../constants';
import { MSAL_GUARD_CONFIG, MsalBroadcastService, MsalGuard, MsalGuardConfiguration, MsalService } from '@azure/msal-angular';
import { InteractionType } from '@azure/msal-browser';
import { Location } from '@angular/common';

@Injectable({
    providedIn: 'root',
})
export class AuthorizedUserGuard extends MsalGuard implements CanActivate   {
    jwtHelper: JwtHelperService;
    parentRouter!: Router;
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
        this.jwtHelper = new JwtHelperService();
    }

    override canActivate(
        route: ActivatedRouteSnapshot, 
        state: RouterStateSnapshot
      ): Observable<boolean | UrlTree> {
        // First check if the user is authenticated with MSAL
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
            catchError(error => {
              console.error('Auth guard error:', error);
              return of(this.parentRouter.createUrlTree(['/home']));
            }));
        
      }

    //   private checkTokenAndClaims(state: RouterStateSnapshot): Promise<boolean | UrlTree> {
    //     return this.authCoreService.getAuthToken()
    //       .then(token => {
    //         const isLoggedIn = !this.authCoreService.accessExpired();
            
    //         if (!isLoggedIn) {
    //           // Token expired, clear claims and redirect to login
    //           this.accountData.clearClaims();
    //           sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
    //           this.authCoreService.login();
    //           return false;
    //         }
            
            
    //         // Check authorization based on claims
    //         const isAuthorized = this.accountData.isAdmin() || this.accountData.isAuthorized();
            
    //         if (!isAuthorized) {
    //           // User is authenticated but not authorized
    //           this.parentRouter.navigate(['/unauthorized']);
    //           return false;
    //         }
            
    //         return true;
    //       })
    //       .catch(error => {
    //         this.accountData.clearClaims();
            
    //         if (error.errorCode === 'no_account_error') {
    //           sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
    //           this.authCoreService.login();
    //           return false;
    //         }
            
    //         this.parentRouter.navigate(['/home']);
    //         return false;
    //       });
    //   }


private async checkTokenAndClaims(state: RouterStateSnapshot): Promise<boolean | UrlTree> {
    try {
      // First get the token - this ensures we're authenticated
      const token = await this.authCoreService.getAuthToken();
      
      // Check if token is expired
      const isLoggedIn = !this.authCoreService.accessExpired();
      if (!isLoggedIn) {
        // Token expired, clear claims and redirect to login
        this.accountData.clearClaims();
        sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
        this.authCoreService.login();
        return false;
      }
      
      // Check if claims are already loaded
      if (this.accountData.hasClaims()) {
        // Claims already exist, check authorization
        const isAuthorized = this.accountData.isAdmin() || this.accountData.isAuthorized();
        if (!isAuthorized) {
          // User is authenticated but not authorized
          return this.parentRouter.createUrlTree(['/unauthorized']);
        }
        console.log('cached is Authorized to view pages')
        return true;
      }
      
      // Claims not loaded yet, force loading them
      try {
        // This will load claims from backend and should return whether user is authorized
        const isAuthorized = await this.accountData.initializeClaims();
        if (!isAuthorized) {
          return this.parentRouter.createUrlTree(['/unauthorized']);
        }
        console.log('api call is Authorized to view pages')
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

    // override canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> {
    //     return this.authCoreService
    //         .getAuthToken()
    //         .then(token => {
    //             const isLoggedIn = !this.authCoreService.accessExpired();
    //             if (!isLoggedIn) {
    //                 // claims need to include user id in name so the someone else's claims can't be reused
    //                 this.accountData.clearClaims();
    //                 sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
    //                 this.authCoreService.login();
    //                 return false;
    //             }
    //             // Check if token has expired, if so, return false
    //             return this.accountData.isAdmin() || this.accountData.isAuthorized();
    //         })
    //         .catch(error => {
    //             this.accountData.clearClaims();
    //             if (error.errorCode === 'no_account_error') {
    //                 sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
    //                 this.authCoreService.login();
    //                 return false;
    //             }
    //             this.parentRouter.navigate(['/home']);
    //             return false;
    //         });
    // }
}


// import { Injectable } from '@angular/core';
// import { Router, CanLoad, Route, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
// import { Observable } from 'rxjs';
// import { JwtHelperService } from '@auth0/angular-jwt';
// import { ClaimsService, MsalService } from '@master-list/auth';
// import { environment } from '@master-list/environments';
// import * as CONST from '../constants';

// @Injectable({
//     providedIn: 'root',
// })
// export class AuthorizedUserGuard implements CanActivate {
//     jwtHelper: JwtHelperService;
//     constructor(
//         private authService: MsalService,
//         private accountData: ClaimsService,
//         private router: Router,
//     ) {
//         this.jwtHelper = new JwtHelperService();
//     }

//     canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Promise<boolean> {
//         return this.authService
//             .getAuthToken()
//             .then(token => {
//                 const isLoggedIn = !this.authService.accessExpired();
//                 if (!isLoggedIn) {
//                     // claims need to include user id in name so the someone else's claims can't be reused
//                     this.accountData.clearClaims();
//                     sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
//                     this.authService.login();
//                     return false;
//                 }
//                 // Check if token has expired, if so, return false
//                 return this.accountData.isAdmin() || this.accountData.isAuthorized();
//             })
//             .catch(error => {
//                 this.accountData.clearClaims();
//                 if (error.errorCode === 'no_account_error') {
//                     sessionStorage.setItem(CONST.REDIRECT_URL_KEY, state.url);
//                     this.authService.login();
//                     return false;
//                 }
//                 this.router.navigate(['/home']);
//                 return false;
//             });
//     }
// }
