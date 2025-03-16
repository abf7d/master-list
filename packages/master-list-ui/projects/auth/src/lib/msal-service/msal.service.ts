// import { Inject, Injectable } from '@angular/core';
// import { AuthStateService } from '../auth-state/auth-state';
// import { BehaviorSubject } from 'rxjs';
// import * as Msal from '@azure/msal-browser';
// import { MsalConfigFactoryService } from '../msal-config-factory/msal-config-factory.service';
// import { ClaimsService } from '../claims-service/claims.service';
// import { environment } from '@master-list/environments';
// import * as CONST from '../constants';
// @Injectable({
//     providedIn: 'root',
// })
// export class MsalService {
//     private loginRequest: Msal.RedirectRequest;
//     private accessTokenRequest: Msal.SilentRequest;
//     private logoutRequest: Msal.EndSessionRequest;
//     public isLoggedIn$: BehaviorSubject<boolean | null>;
//     private msalInstance: Msal.PublicClientApplication;

//     constructor(
//         private claimsService: ClaimsService,
//         private authState: AuthStateService,
//         configFactory: MsalConfigFactoryService,
//     ) {
//         this.loginRequest = {
//             scopes: environment.loginScopes,
//             extraScopesToConsent: [environment.exposedApiScope],
//         };
//         this.accessTokenRequest = {
//             scopes: [environment.exposedApiScope],
//             account: undefined,
//             forceRefresh: false // experiment with this for refresh, look this up
//         };
//         this.logoutRequest = {
//             postLogoutRedirectUri: environment.postLogoutUrl,
//         };
//         this.isLoggedIn$ = authState.isLoggedIn$;
//         const msalConfig = configFactory.get();
//         this.msalInstance = new Msal.PublicClientApplication(msalConfig);
//         this.msalInstance
//             .handleRedirectPromise()
//             .then((tokenResponse: Msal.AuthenticationResult | null) => {
//                 if (tokenResponse !== null) {
//                     const accountObj = tokenResponse.account;
//                     if (accountObj !== null) {
//                         this.accessTokenRequest.account = accountObj;
//                     }
//                     this.acquireSilent(this.accessTokenRequest);
//                 }
//             })
//             .catch(error => {
//                 authState.loginError$.next(true);
//                 console.error(error);
//                 claimsService.setError(true);
//             });
//     }

//     private acquireSilent(request: Msal.SilentRequest): Promise<Msal.AuthenticationResult | null> {
//         const authState = this.authState;
//         const claimService = this.claimsService;
//         return this.msalInstance.acquireTokenSilent(request).then(
//             access_token => {
//                 if (!access_token.accessToken) {
//                     this.msalInstance.acquireTokenRedirect(request);
//                     this.authState.loginError$.next(true);
//                     this.claimsService.setError(true);
//                 } else {
//                     sessionStorage.removeItem(CONST.CLAIMS_TOKEN_CACHE_KEY);
//                     this.claimsService.initializeClaims().then(
//                         isAuthorized => {
//                             this.authState.isAuthorized$.next(isAuthorized);
//                         },
//                         reason => {
//                             if (reason.status === 401) {
//                                 this.authState.isAuthorized$.next(false);
//                                 this.authState.isLoggedIn$.next(false);
//                                 return;
//                             }
//                             console.error('claims error:', reason);
//                             this.authState.loginError$.next(true);
//                         },
//                     );
//                     this.isLoggedIn$.next(true);
//                 }
//                 return access_token;
//             },
//             function (reason) {
//                 console.error(reason);
//                 authState.loginError$.next(true);
//                 claimService.setError(true);
//                 return null;
//             },
//         );
//     }

//     public login(): void {
//         this.msalInstance.loginRedirect(this.loginRequest);
//     }

//     public accessExpired(): boolean {
//         return !this.msalInstance.getAllAccounts()[0];
//     }

//     public getAuthToken(): Promise<Msal.AuthenticationResult> {
//         const accounts = this.msalInstance.getAllAccounts();
//         this.accessTokenRequest.account = accounts[0];
//         return this.msalInstance.acquireTokenSilent(this.accessTokenRequest);
//     }

//     public logout(): void {
//         this.authState.loginError$.next(false);
//         this.claimsService.clearError();
//         this.claimsService.clearClaims();
//         this.msalInstance.logout(this.logoutRequest);
//     }

//     public loadUserGroups(): Promise<any> {
//         return this.claimsService.initializeClaims();
//     }

//     public getUserName(): string {
//         const account = this.msalInstance.getAllAccounts()[0];
//         if (account && account.name !== undefined) {
//             return account.name;
//         }
//         return '';
//     }

//     public hasClaims(): boolean {
//         return this.claimsService.hasClaims();
//     }

//     public isAuthorized(): boolean {
//         return this.claimsService.isAuthorized();
//     }

//     public hasError(): boolean {
//         return this.claimsService.hasError();
//     }

//     public ensureRedirectCompleted(): Promise<boolean> {
//         return this.msalInstance
//             .handleRedirectPromise()
//             .then(response => {
//                 // True if the user is authenticated, false otherwise
//                 return !!response && !!response.account;
//             })
//             .catch(error => {
//                 console.error('Error during redirect handling:', error);
//                 return false;
//             });
//     }
//     public isAuthenticated(): boolean {
//         const accounts = this.msalInstance.getAllAccounts();
//         return accounts && accounts.length > 0;
//     }
// }
