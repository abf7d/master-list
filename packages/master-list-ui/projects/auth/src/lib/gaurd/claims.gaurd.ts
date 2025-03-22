// // claims.guard.ts
// import { Injectable } from '@angular/core';
// import {
//   ActivatedRouteSnapshot,
//   Router,
//   RouterStateSnapshot,
//   UrlTree,
// } from '@angular/router';
// import { MsalGuard } from '@azure/msal-angular';
// import { Observable, of } from 'rxjs';
// import { catchError, map, switchMap } from 'rxjs/operators';
// import { AuthService } from './auth.service';
// import { ClaimsService } from './claims.service';

// @Injectable({
//   providedIn: 'root',
// })
// export class ClaimsGuard extends MsalGuard {
//   constructor(
//     private authService: AuthService,
//     private claimsService: ClaimsService,
//     private router: Router
//   ) {
//     super();
//   }

//   override canActivate(
//     route: ActivatedRouteSnapshot,
//     state: RouterStateSnapshot
//   ):
//     | Observable<boolean | UrlTree>
//     | Promise<boolean | UrlTree>
//     | boolean
//     | UrlTree {
//     // First check if user is authenticated with MSAL
//     return super.canActivate(route, state).pipe(
//       switchMap((canActivate: boolean) => {
//         if (!canActivate) {
//           return of(false);
//         }

//         // User is authenticated, now fetch claims from backend
//         return this.claimsService.fetchUserClaims().pipe(
//           map((claims) => {
//             if (!claims) {
//               // No claims found, redirect to unauthorized page
//               return this.router.createUrlTree(['/unauthorized']);
//             }

//             // Check required roles if specified in route data
//             const requiredRoles = route.data['requiredRoles'] as string[];
//             if (requiredRoles && requiredRoles.length > 0) {
//               const hasRole = requiredRoles.some(
//                 (role) => claims.roles && claims.roles.includes(role)
//               );

//               if (!hasRole) {
//                 return this.router.createUrlTree(['/unauthorized']);
//               }
//             }

//             return true;
//           }),
//           catchError(() => {
//             // Error fetching claims
//             return of(this.router.createUrlTree(['/unauthorized']));
//           })
//         );
//       })
//     );
//   }
// }
