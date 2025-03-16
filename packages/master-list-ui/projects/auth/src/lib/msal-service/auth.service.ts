import { Inject, Injectable } from "@angular/core";
import { MSAL_GUARD_CONFIG, MsalBroadcastService, MsalGuardConfiguration, MsalService } from "@azure/msal-angular";
import { AuthenticationResult, EventMessage, EventType, InteractionType, PopupRequest, RedirectRequest } from "@azure/msal-browser";
import { environment } from "@master-list/environments";
import * as Msal from '@azure/msal-browser';
import { filter, Subject, Subscription, takeUntil } from "rxjs";

type IdTokenClaimsWithPolicyId = Msal.IdTokenClaims & {
    acr?: string,
    tfp?: string,
};

export const accessTokenRequest: Msal.SilentRequest = {
    scopes: [environment.exposedApiScope],
    account: undefined
};
@Injectable({
    providedIn: 'root',
})
export class AuthCoreService {
    sub!: Subscription;
   
    constructor( private authService: MsalService ){
    }
    public login () {
        let signUpSignInFlowRequest: RedirectRequest | PopupRequest  = {
            authority: environment.b2cPolicies.authorities.signUpSignIn.authority,
            scopes: [...environment.apiConfig.scopes],
        };
        const userFlowRequest = signUpSignInFlowRequest;
        this.authService.loginRedirect(userFlowRequest);
    }

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
}