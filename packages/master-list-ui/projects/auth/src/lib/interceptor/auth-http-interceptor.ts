import { from, Observable } from 'rxjs';
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { JwtHelperService } from '@auth0/angular-jwt';
import { catchError, switchMap } from 'rxjs/operators';
import { MsalService } from '../msal-service/msal.service';
import { LoggerService } from '../logger/logger.service';

@Injectable()
export class AuthHttpInterceptor implements HttpInterceptor {
    jwtHelper: JwtHelperService;
    constructor(
        private authenticationService: MsalService,
        private logger: LoggerService,
    ) {
        this.jwtHelper = new JwtHelperService();
    }

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        return from(this.authenticationService.getAuthToken()).pipe(
            switchMap(token => {
                const existingBearer = req.headers.get('Authorization');
                if (!existingBearer) {
                    req = req.clone({
                        setHeaders: {
                            Authorization: `Bearer ${token.accessToken}`,
                        },
                    });
                }
                return next.handle(req);
            }),
            catchError(error => {
                this.logger.info('Problem fetching the auth token, not including in header', error);
                return next.handle(req);
            }),
        );
    }
}
