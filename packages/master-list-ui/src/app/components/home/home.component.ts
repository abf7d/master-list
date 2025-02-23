import { CommonModule } from '@angular/common';
import { Component, HostListener } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthStateService, MsalService } from '@master-list/auth';
import { BehaviorSubject, catchError, from, map, Observable, of } from 'rxjs';

export const COOKIES_BLOCKED_ID: string = 'MM:3PCunsupported';
export const COOKIES_AVAIL_ID: string = 'MM:3PCsupported';

@Component({
  selector: 'app-home',
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  public isLoggedIn$: BehaviorSubject<boolean | null>;
  public online$: Observable<boolean>;
  public name!: string;
  public isLoggedIn!: boolean;
  public thirdPartyCookiesBlocked: boolean;

  constructor(
      private authService: MsalService,
      private authStore: AuthStateService,
  ) {
      this.isLoggedIn$ = this.authStore.isLoggedIn$;
      this.thirdPartyCookiesBlocked = false;
      this.online$ = this.checkInternetConnection();
  }

  public ngOnInit() {
      this.isLoggedIn$.subscribe((loggedIn: boolean | null) => {
          this.name = this.authService.getUserName() ?? '';
          this.isLoggedIn = !!loggedIn && !this.authService.accessExpired();
      });
  }

  public login() {
      this.authService.login();
  }

  public logout() {
      this.authService.logout();
  }

  @HostListener('window:message', ['$event'])
  public receiveMessage(event: any) {
      if (event.data === COOKIES_BLOCKED_ID) {
          this.thirdPartyCookiesBlocked = true;
      } else if (event.data === COOKIES_AVAIL_ID) {
          this.thirdPartyCookiesBlocked = false;
      }
  }

  private checkInternetConnection(): Observable<boolean> {
      return from(fetch('https://cors-anywhere.herokuapp.com/https://www.google.com')).pipe(
          map(() => true),
          catchError(() => of(false)),
      );
  }
}
