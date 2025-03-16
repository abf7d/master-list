// import { Injectable } from '@angular/core';
// import { Router, CanActivate } from '@angular/router';
// import { combineLatest, filter, firstValueFrom, forkJoin, map } from 'rxjs';
// import { JwtHelperService } from '@auth0/angular-jwt';
// import { AuthStateService, ClaimsService, MsalService } from '@master-list/auth';
// import { REDIRECT_URL_KEY } from '../constants';

// @Injectable({
//     providedIn: 'root',
// })
// export class RedirectGuard implements CanActivate {
//     jwtHelper: JwtHelperService;
//     constructor(
//         private authService: MsalService,
//         private router: Router,
//         private authStore: AuthStateService,
//     ) {
//         this.jwtHelper = new JwtHelperService();
//     }

//     canActivate(): Promise<boolean> {
//         return this.authService.ensureRedirectCompleted().then((isAuthenticated: boolean) => {
//             const observable$ = combineLatest([this.authStore.isLoggedIn$, this.authStore.isAuthorized$, this.authStore.loginError$]).pipe(
//                 filter(([isLoggedIn, isAuthorized, loginError]) => isLoggedIn !== null && (isAuthorized !== null || loginError !== null)),
//                 map(([isLoggedIn, isAuthorized, loginError]) => {
//                     if (loginError) {
//                         this.router.navigate(['/login-error']);
//                         return true;
//                     }
//                     if (isAuthorized) {
//                         const rediect = this.checkRedirectUrl();
//                         if (rediect) {
//                             return true;
//                         }
//                         if (this.authStore.redirectUrl) {
//                             const rediectUrl = this.authStore.redirectUrl;
//                             this.authStore.redirectUrl = null;
//                             this.router.navigateByUrl(rediectUrl);
//                             return true;
//                         }

//                         this.router.navigate(['/main']);
//                         return true;
//                     } else {
//                         this.router.navigate(['/request-access']);
//                         return true;
//                     }
//                 }),
//             );
//             return firstValueFrom(observable$);
//         });
//     }

//     private checkRedirectUrl(): boolean {
//         let redirectUrl = sessionStorage.getItem(REDIRECT_URL_KEY);

//         //THIS IS NOT WORKING, IT IS GETTING THE URL FROM THE REDIRECT URL KEY, BuT is not redirecting to the url
//         if (redirectUrl) {
//             this.authStore.redirectUrl = redirectUrl;
//             redirectUrl = this.stripBaseHref(redirectUrl);
//             sessionStorage.removeItem(REDIRECT_URL_KEY); // Clear the stored URL
//             this.router.navigateByUrl(redirectUrl);
//             return true;
//         }
//         return false;
//     }

//     private stripBaseHref(url: string): string {
//         const baseHref = this.router.url.slice(0, this.router.url.indexOf('/', 1));
//         if (url.startsWith(baseHref)) {
//             return url.slice(baseHref.length);
//         }
//         return url;
//     }
// }
