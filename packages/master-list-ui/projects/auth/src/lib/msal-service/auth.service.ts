import { Inject, Injectable } from '@angular/core';
import { MSAL_GUARD_CONFIG, MSAL_INSTANCE, MsalBroadcastService, MsalGuardConfiguration, MsalService } from '@azure/msal-angular';
import { AuthenticationResult, EventMessage, EventType, InteractionType, PopupRequest, RedirectRequest } from '@azure/msal-browser';
import { environment } from '@master-list/environments';
import * as Msal from '@azure/msal-browser';
import { filter, Subject, Subscription, takeUntil } from 'rxjs';
import { ClaimsService } from '../claims-service/claims.service';
import { AuthStateService } from '../auth-state/auth-state';

type IdTokenClaimsWithPolicyId = Msal.IdTokenClaims & {
    acr?: string;
    tfp?: string;
};

export const accessTokenRequest: Msal.SilentRequest = {
    scopes: [environment.exposedApiScope],
    account: undefined,
};
@Injectable({
    providedIn: 'root',
})
export class AuthCoreService {
    sub!: Subscription;
    private loginRequest: Msal.RedirectRequest;
    private accessTokenRequest: Msal.SilentRequest;
    private logoutRequest: Msal.EndSessionRequest;
    // private msalInstance!: Msal.IPublicClientApplication;

    constructor(
        private msalService: MsalService,
        private claimsService: ClaimsService,
        private authState: AuthStateService,
        private msalBroadcastService: MsalBroadcastService,

        @Inject(MSAL_INSTANCE) private msalInstance: Msal.IPublicClientApplication,
    ) {
        // this.msalInstance = msalConfig; //this.MSALInstanceFactory();

        this.loginRequest = {
            scopes: environment.loginScopes,
            extraScopesToConsent: [environment.exposedApiScope],
        };
        this.accessTokenRequest = {
            scopes: [environment.exposedApiScope],
            account: undefined,
            forceRefresh: false, // experiment with this for refresh, look this up
        };
        this.logoutRequest = {
            postLogoutRedirectUri: environment.postLogoutUrl,
        };

        // this.checkAndLoadClaims();

        // // Set up event listeners for MSAL events
        // this.setupAuthEventHandlers();

        // this.msalBroadcastService.msalSubject$
        //     .pipe(
        //         filter((msg: EventMessage) => msg.eventType === Msal.EventType.INITIALIZE_END),
        //         takeUntil(this.destroying$),
        //     )
        //     .subscribe(() => {
        //         // MSAL is now initialized, safe to proceed
        //         this.checkAndLoadClaims();
        //         this.setupAuthEventHandlers();
        //     });
    }

    loggerCallback(logLevel: Msal.LogLevel, message: string) {
        console.log(message);
    }

    public login() {
        let signUpSignInFlowRequest: RedirectRequest | PopupRequest = {
            authority: environment.b2cPolicies.authorities.signUpSignIn.authority,
            scopes: [...environment.apiConfig.scopes],
        };
        const userFlowRequest = signUpSignInFlowRequest;
        this.msalService.loginRedirect(userFlowRequest);
    }

    public getAuthToken(): Promise<Msal.AuthenticationResult> {
        const accounts = this.msalInstance.getAllAccounts();
        this.accessTokenRequest.account = accounts[0];
        return this.msalInstance.acquireTokenSilent(this.accessTokenRequest);
    }
    public accessExpired(): boolean {
        return !this.msalInstance.getAllAccounts()[0];
    }

    public logout(): void {
        this.authState.loginError$.next(false);
        this.claimsService.clearError();
        this.claimsService.clearClaims();
        this.msalInstance.logout(this.logoutRequest);
    }

    public hasClaims(): boolean {
        return this.claimsService.hasClaims();
    }

    public isAuthorized(): boolean {
        return this.claimsService.isAuthorized();
    }

    public hasError(): boolean {
        return this.claimsService.hasError();
    }

    public isAuthenticated(): boolean {
        const accounts = this.msalInstance.getAllAccounts();
        return accounts && accounts.length > 0;
    }

    private readonly destroying$ = new Subject<void>();
    ngOnDestroy(): void {
        this.destroying$.next();
        this.destroying$.complete();
    }

    // private checkAndLoadClaims(): void {
    //     // Check if user is logged in
    //     const accounts = this.msalService.instance.getAllAccounts();
    //     if (accounts.length > 0) {
    //         this.loadUserClaims();
    //     }
    // }

    // private setupAuthEventHandlers(): void {
    //     // Listen for login success events
    //     this.msalBroadcastService.msalSubject$
    //         .pipe(
    //             filter((msg: EventMessage) => msg.eventType === EventType.LOGIN_SUCCESS),
    //             takeUntil(this.destroying$),
    //         )
    //         .subscribe(() => {
    //             // User has successfully logged in, fetch claims
    //             this.loadUserClaims();
    //         });

    //     // Listen for interaction completion events
    //     this.msalBroadcastService.inProgress$
    //         .pipe(
    //             filter((status: Msal.InteractionStatus) => status === Msal.InteractionStatus.None),
    //             takeUntil(this.destroying$),
    //         )
    //         .subscribe(() => {
    //             // Only load claims if the user is logged in
    //             const accounts = this.msalService.instance.getAllAccounts();
    //             if (accounts.length > 0) {
    //                 this.loadUserClaims();
    //             }
    //         });
    // }

    // loadUserClaims(): void {
    //     // First ensure we have a valid token
    //     const accounts = this.msalService.instance.getAllAccounts();
    //     if (accounts.length === 0) return;

    //     const account = accounts[0];

    //     this.msalService.instance
    //         .acquireTokenSilent({
    //             scopes: [...environment.apiConfig.scopes],
    //             account: account,
    //         })
    //         .then(
    //             token => {
    //                 if (token) {
    //                     // Token acquired successfully, now fetch claims
    //                     this.claimsService.initializeClaims().then(
    //                         isAuthorized => {
    //                             console.log('Claims loaded, authorized:', isAuthorized);
    //                             // You can update any state here if needed
    //                         },
    //                         error => {
    //                             console.error('Error loading claims:', error);
    //                             if (error.status === 401) {
    //                                 // Handle unauthorized
    //                                 this.claimsService.clearClaims();
    //                             }
    //                         },
    //                     );
    //                 }
    //             },
    //             error => {
    //                 console.error('Error acquiring token silently:', error);
    //                 // Handle token acquisition errors
    //                 this.claimsService.setError(true);
    //             },
    //         );
    // }
}

// this.authService
//         .getAuthToken()
//         .then(token => {
//             const isLoggedIn = !this.authService.accessExpired();

//     public initAccesTokenRetrieval(){
//          this.sub = this.msalBroadcastService.msalSubject$
//             .pipe(
//                 filter((msg: EventMessage) => msg.eventType === EventType.LOGIN_SUCCESS
//                     || msg.eventType === EventType.ACQUIRE_TOKEN_SUCCESS
//                     || msg.eventType === EventType.SSO_SILENT_SUCCESS),
//                 takeUntil(this._destroying$)
//             )
//             .subscribe((result: EventMessage) => {

//                 let payload = result.payload as AuthenticationResult;
//                 let idtoken = payload.idTokenClaims as IdTokenClaimsWithPolicyId;
//                 accessTokenRequest.account = payload.account;
//                 if (idtoken.acr === environment.b2cPolicies.names.signUpSignIn || idtoken.tfp === environment.b2cPolicies.names.signUpSignIn) {
//                     this.authService.instance.setActiveAccount(payload.account);

//                     this.authService.acquireTokenSilent(accessTokenRequest).subscribe( access_token => {
//                         console.log('1234 access_token', access_token)
//                         const cache = this.authService.instance.getTokenCache();
//                     //   this.claimsService.initializeClaims().then(
//                     //     isAuthorized => {
//                     //       console.log(isAuthorized)
//                     //         // this.authState.isAuthorized$.next(isAuthorized);
//                     //     },
//                     //     reason => {
//                     //         if (reason.status === 401) {
//                     //             // this.authState.isAuthorized$.next(false);
//                     //             // this.authState.isLoggedIn$.next(false);
//                     //             return;
//                     //         }
//                     //         console.error('claims error:', reason);
//                     //         // this.authState.loginError$.next(true);
//                     //     },
//                 //     );
//                 //    })

//                 //    const cache = this.authService.instance.getTokenCache();
//                     console.log('payload.accessToken', payload.accessToken)

//                     //  const httpOptions = {
//                     //   headers: new HttpHeaders({
//                     //     'Content-Type':  'application/json',
//                     //     Authorization: 'Bearer '+payload.accessToken
//                     //   })}

//                     // this.http.get("https://graph.microsoft.com/v1.0/groups?$select=id,displayName",httpOptions).toPromise().then(result=>{console.log(result)});
//             //    }

//                     return result;
//                 });
//             }
//         });
//     }
// }
