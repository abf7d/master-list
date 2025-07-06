import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent,
} from '@angular/common/http';
import { Observable, firstValueFrom, from, of, throwError } from 'rxjs';
import {
  catchError,
  filter,
  map,
  skipUntil,
  switchMap,
  take,
} from 'rxjs/operators';
import { MsalService } from '@azure/msal-angular';
import { AuthenticationResult, InteractionType } from '@azure/msal-browser';
import { environment } from '@env/environment';

@Injectable()
export class MsalManualInterceptor implements HttpInterceptor {
  private accessToken: AuthenticationResult | null = null;
  private tokenExpiration: Date | null = null;

  constructor(private authService: MsalService) {}

  intercept(
    req: HttpRequest<any>,
    next: HttpHandler,
  ): Observable<HttpEvent<any>> {
    return this.getTokenSilently().pipe(
      switchMap((token) => {
        console.log(token);
        // Clone the request and add the authorization header
        const authReq = req.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`,
          },
        });

        // Pass the cloned request to the next handler
        return next.handle(authReq);
      }),
      catchError((error) => {
        console.error('Error acquiring token silently:', error);
        // Return the original request if token acquisition fails
        // Or you could implement custom error handling here
        return next.handle(req);
      }),
    );
  }

  private getTokenSilently(): Observable<string> {
    if (this.accessToken) {
      return of(this.accessToken.accessToken);
    }

    const request = {
      // It was important to use environment.exposeApiScope instead of environment.apiConfig.scopes
      scopes: [environment.exposedApiScope],
      account: this.authService.instance.getAllAccounts()[0],
      forceRefresh: false,
    };

    return this.authService.acquireTokenSilent(request).pipe(
      map((result) => result?.accessToken || ''), // Extract token, default to empty string
      catchError((error) => {
        console.error('Token acquisition error:', error);
        return of(''); // Return empty observable to avoid breaking the request flow
      }),
    );
  }
}
