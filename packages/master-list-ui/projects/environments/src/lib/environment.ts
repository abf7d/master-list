import { NgxLoggerLevel } from 'ngx-logger';

export const environment = {
    clientDeugLevel: 1, // 1 is debug
    serverDebugLevel: 7, // 7 is off
    serverLoggerApi: 'https://localhost:44393/api/logger',
    baseUrl: 'https://localhost:4200/tes',
    production: false,
    // Arrow building api is now functions
    mappingApi: 'http://localhost:7071/api/',
    projectBuilderApi: 'https://localhost:44393/api/',
    authority: 'https://criticalplayground.b2clogin.com/criticalplayground.onmicrosoft.com/B2C_1_DefaultSignInSignUp2',
    knownAuthorities: ['criticalplayground.b2clogin.com'],
    redirectUri:  'https://localhost:4200/main', // 'https://localhost:4200/login-redirect',
    cacheLocation: 'sessionStorage',
    loginScopes: ['openid', 'offline_access'],
    exposedApiScope: 'https://criticalplayground.onmicrosoft.com/api/read',
    postLogoutUrl: 'https://localhost:4200/logout/', //'https://localhost:4200/home/',
    clientID: '7515b8bc-44ba-4f60-9740-62b9ac197bf3',
    payPalClientId: 'AUyE2UNCsa6sgAKS3Ccj4WUzXw-PisRoJL2zn9pzxbN5sje0xalPOx9ioUCug9sK6HQF9Vybu2Bh_4LB',

    // Main api in dev is now not over https
    // criticalPathApi: 'http://localhost:7071/api/', 
    masterListApi: 'http://127.0.0.1:8000/',
    webApi: 'https://localhost:44369/api/', 

    jiraClientId: '1SdMM8pTryWCljI1Awm9drfKvnU2BR2H',
    jiraClientSecret: '123',
    logLevel: NgxLoggerLevel.INFO,
    appInsightsInstrKey: '1fed53fa-9630-48dc-b30c-7c4685489b46',
    appInsightsOn: false,
    enableInDevEnv: true,
};
