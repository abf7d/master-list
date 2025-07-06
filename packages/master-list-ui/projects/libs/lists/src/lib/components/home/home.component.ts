import { CommonModule } from '@angular/common';
import { Component, HostListener, Inject, OnDestroy, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthStateService } from '@auth/auth-state/auth-state';
import { AuthCoreService } from '@auth/auth-service/auth.service';
import { BehaviorSubject, catchError, filter, from, map, Observable, of, Subject, Subscription, takeUntil } from 'rxjs';

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
     private authService: AuthCoreService,
      private authStore: AuthStateService,
  ) {
      this.isLoggedIn$ = this.authStore.isLoggedIn$;
      this.thirdPartyCookiesBlocked = false;
      this.online$ = this.checkInternetConnection();
  }

  loginClicked() {
    this.authService.login();
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

  public logout() {
    this.authService.logout()
  }
}
