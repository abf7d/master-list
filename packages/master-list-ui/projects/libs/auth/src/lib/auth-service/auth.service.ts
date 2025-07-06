import { Inject, Injectable } from '@angular/core';
import { MSAL_INSTANCE, MsalService } from '@azure/msal-angular';
import { PopupRequest, RedirectRequest } from '@azure/msal-browser';
import * as Msal from '@azure/msal-browser';
import { Subject, Subscription } from 'rxjs';
import { ClaimsService } from '../claims-service/claims.service';
import { AuthStateService } from '../auth-state/auth-state';
import * as CONST from '../constants';
import { environment } from '@env/environment';

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
    private readonly destroying$ = new Subject<void>();

    constructor(
        private msalService: MsalService,
        private claimsService: ClaimsService,
        private authState: AuthStateService,

        @Inject(MSAL_INSTANCE) private msalInstance: Msal.IPublicClientApplication,
    ) {
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

    public acquireSilent(): Promise<Msal.AuthenticationResult | null> {
        const authState = this.authState;
        const claimService = this.claimsService;
        return this.msalInstance.acquireTokenSilent(this.accessTokenRequest).then(
            access_token => {
                if (!access_token.accessToken) {
                    this.msalInstance.acquireTokenRedirect(accessTokenRequest);
                    this.authState.loginError$.next(true);
                    this.claimsService.setError(true);
                } else {
                    sessionStorage.removeItem(CONST.CLAIMS_TOKEN_CACHE_KEY);
                    this.claimsService.initializeClaims().then(
                        isAuthorized => {
                            this.authState.isAuthorized$.next(isAuthorized);
                        },
                        reason => {
                            if (reason.status === 401) {
                                this.authState.isAuthorized$.next(false);
                                this.authState.isLoggedIn$.next(false);
                                return;
                            }
                            console.error('claims error:', reason);
                            this.authState.loginError$.next(true);
                        },
                    );
                }
                return access_token;
            },
            function (reason) {
                console.error(reason);
                authState.loginError$.next(true);
                claimService.setError(true);
                return null;
            },
        );
    }

    ngOnDestroy(): void {
        this.destroying$.next();
        this.destroying$.complete();
    }
}
