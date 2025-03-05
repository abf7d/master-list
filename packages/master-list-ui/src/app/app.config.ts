import {
  ApplicationConfig,
  ErrorHandler,
  importProvidersFrom,
  provideZoneChangeDetection,
} from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import {
  HTTP_INTERCEPTORS,
  provideHttpClient,
  withInterceptorsFromDi,
} from '@angular/common/http';

import { AuthHttpInterceptor, CanDeactivateGuard } from '@master-list/auth';
import { environment } from '@master-list/environments';
import { provideToastr } from 'ngx-toastr';
import { provideAnimations } from '@angular/platform-browser/animations';
import { LoggerModule } from 'ngx-logger';
import { LoggerService } from '@master-list/auth';
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(),
    provideAnimations(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthHttpInterceptor,
      multi: true,
    },
    provideHttpClient(withInterceptorsFromDi()),
    // provideAnimations(),
    importProvidersFrom(LoggerModule.forRoot({ level: environment.logLevel })),
    { provide: ErrorHandler, useClass: LoggerService },

    CanDeactivateGuard,
    provideClientHydration(),
    provideToastr(),
  ],
};
