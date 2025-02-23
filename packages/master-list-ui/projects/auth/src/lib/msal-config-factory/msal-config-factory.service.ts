import * as Msal from '@azure/msal-browser';
import { Injectable } from '@angular/core';
import { environment } from '@master-list/environments';
import { LoggerService } from '../logger/logger.service';
// import { LoggerService } from '@critical-pass/core';
@Injectable({
    providedIn: 'root',
})
export class MsalConfigFactoryService {
    constructor(private logger: LoggerService) {}
    get(): Msal.Configuration {
        return {
            auth: {
                clientId: environment.clientID,
                authority: environment.authority,
                knownAuthorities: environment.knownAuthorities,

                redirectUri: environment.redirectUri,
                navigateToLoginRequestUrl: false,
            },
            cache: {
                cacheLocation: environment.cacheLocation,
                storeAuthStateInCookie: false, // Set this to "true" to save cache in cookies to address trusted zones limitations in IE (see: https://github.com/AzureAD/microsoft-authentication-library-for-js/wiki/Known-issues-on-IE-and-Edge-Browser)
            },
            system: {
                loggerOptions: {
                    loggerCallback: (level: Msal.LogLevel, message: string, containsPii: boolean): void => {
                        if (containsPii) {
                            return;
                        }
                        switch (level) {
                            case Msal.LogLevel.Error:
                                this.logger.error(message);
                                return;
                            case Msal.LogLevel.Info:
                                this.logger.info(message);
                                return;
                            case Msal.LogLevel.Verbose:
                                this.logger.debug(message);
                                return;
                            case Msal.LogLevel.Warning:
                                this.logger.warn(message);
                                return;
                        }
                    },
                    piiLoggingEnabled: true,
                },
                windowHashTimeout: 60000,
                iframeHashTimeout: 6000,
                loadFrameTimeout: 0,
                asyncPopups: false,
            },
        };
    }
}
