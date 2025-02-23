import { NgxLoggerLevel } from 'ngx-logger';

export const environment = {
    production: true,
    clientDeugLevel: 7, // 1 is debug
    serverDebugLevel: 7, // 7 is off
    serverLoggerApi: 'https://<place-holder>',
    baseUrl: 'https://app.criticalpass.io',
    mappingApi: 'https://criticalpassapifunctions.azurewebsites.net/api/', // 'https://criticalpathapi.azurewebsites.net/api/', // for msproj files and building arrow diagram
    authority: 'https://criticalplayground.b2clogin.com/criticalplayground.onmicrosoft.com/B2C_1_DefaultSignInSignUp2',
    knownAuthorities: ['criticalplayground.b2clogin.com'],
    redirectUri: 'https://app.criticalpass.io/login-redirect',
    cacheLocation: 'sessionStorage',
    loginScopes: ['openid', 'offline_access'],
    exposedApiScope: 'https://criticalplayground.onmicrosoft.com/api/read',
    postLogoutUrl: 'https://criticalpass.io',
    clientID: '7515b8bc-44ba-4f60-9740-62b9ac197bf3',
    payPalClientId: 'AUyE2UNCsa6sgAKS3Ccj4WUzXw-PisRoJL2zn9pzxbN5sje0xalPOx9ioUCug9sK6HQF9Vybu2Bh_4LB',
    criticalPathApi: 'https://criticalpassapifunctions.azurewebsites.net/api/', // 'https://criticalpathapifunctions.azurewebsites.net/api/',
    jiraClientId: '1SdMM8pTryWCljI1Awm9drfKvnU2BR2H',
    jiraClientSecret: '123',
    logLevel: NgxLoggerLevel.ERROR,
    appInsightsInstrKey: '1fed53fa-9630-48dc-b30c-7c4685489b46',
    appInsightsOn: true,
    enableInDevEnv: false,
};
