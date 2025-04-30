import {
  ApplicationConfig,
  ErrorHandler,
  importProvidersFrom,
  Injectable,
  provideZoneChangeDetection,
} from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import {
  HTTP_INTERCEPTORS,
  HttpContextToken,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  provideHttpClient,
  withFetch,
  withInterceptorsFromDi,
} from '@angular/common/http';

import { environment } from '@master-list/environments';
import { provideToastr } from 'ngx-toastr';
import { provideAnimations } from '@angular/platform-browser/animations';
import { LoggerModule } from 'ngx-logger';
import { LoggerService } from '@master-list/auth';
import { provideClientHydration } from '@angular/platform-browser';
import { HashLocationStrategy, LocationStrategy } from '@angular/common';





import {
  IPublicClientApplication,
  PublicClientApplication,
  InteractionType,
  BrowserCacheLocation,
  LogLevel,
} from '@azure/msal-browser';
import {
  MsalInterceptor,
  MSAL_INSTANCE,
  MsalInterceptorConfiguration,
  MsalGuardConfiguration,
  MSAL_GUARD_CONFIG,
  MSAL_INTERCEPTOR_CONFIG,
  MsalService,
  MsalGuard,
  MsalBroadcastService,
  MsalInterceptorAuthRequest,
} from '@azure/msal-angular';
import { Observable } from 'rxjs';




export function loggerCallback(logLevel: LogLevel, message: string) {
  console.log(message);
}

export function MSALInstanceFactory(): IPublicClientApplication {
  return new PublicClientApplication({
    auth: {
      clientId: environment.msalConfig.auth.clientId,
      authority: environment.b2cPolicies.authorities.signUpSignIn.authority,
      redirectUri: environment.redirectUri, 
      postLogoutRedirectUri: environment.postLogoutUrl, //'/home',
      knownAuthorities: [environment.b2cPolicies.authorityDomain],
      navigateToLoginRequestUrl: false,
      // navigateToLoginRequestUrl: true, //commenting this out allowed me to refresh the page and it navigated
    },
    cache: {
      cacheLocation: BrowserCacheLocation.SessionStorage, 
    },
    system: {
      allowPlatformBroker: false, // Disables WAM Broker
      loggerOptions: {
        loggerCallback,
        logLevel: LogLevel.Info,
        piiLoggingEnabled: false,
      },
    },
  });
}

export function MSALInterceptorConfigFactory(): MsalInterceptorConfiguration {
  const protectedResourceMap = new Map<string, Array<string>>();
  protectedResourceMap.set(
    environment.apiConfig.uri,
    // This scope was breaking the msalInterceptor. it was environment.apiConfig.scopes but I changed it to below and it works
    [environment.exposedApiScope]
  );

  return {
    interactionType: InteractionType.Redirect,
    protectedResourceMap,
  };
}

export function MSALGuardConfigFactory(): MsalGuardConfiguration {
  return {
    interactionType: InteractionType.Redirect,
    authRequest: {
      scopes: [...environment.apiConfig.scopes],
    },
    loginFailedRoute: '/home',
  };
}

export const BYPASS_MSAL = new HttpContextToken(() => false);

// @Injectable()
// export class CustomMsalInterceptor extends MsalInterceptor implements HttpInterceptor {
//   override intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
//     console.log('request', request.headers)
//     if (request.context.get(BYPASS_MSAL)) {
//       return next.handle(request);
//     }
//     return super.intercept(request, next);
//   }
// }

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(),
    provideAnimations(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
   
    // provideAnimations(),
    importProvidersFrom(LoggerModule.forRoot({ level: environment.logLevel })),
    // { provide: ErrorHandler, useClass: LoggerService },
    provideToastr(),
    provideHttpClient(withInterceptorsFromDi(), withFetch()),
    {
      provide: MSAL_INSTANCE,
      useFactory: MSALInstanceFactory,
    },
    {
      provide: MSAL_GUARD_CONFIG,
      useFactory: MSALGuardConfigFactory,
    },
    {
      provide: MSAL_INTERCEPTOR_CONFIG,
      useFactory: MSALInterceptorConfigFactory,
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: MsalInterceptor, 
      multi: true,
    },
    MsalService,
    MsalGuard,
    MsalBroadcastService,
  ],
};
