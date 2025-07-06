import { Injectable, ErrorHandler } from '@angular/core';
import { NGXLogger, NgxLoggerLevel } from 'ngx-logger';
@Injectable({
    providedIn: 'root',
})
export class LoggerService extends ErrorHandler {
    constructor(private _logger: NGXLogger) {
        super();
    }
    public override handleError(error: any): void {
        this._logger.error(error);
    }
    public trace(message: any, ...additional: any[]): void {
        this._logger.trace(message, additional);
    }

    public debug(message: any, ...additional: any[]): void {
        this._logger.debug(message, additional);
    }

    public info(message: any, ...additional: any[]): void {
        this._logger.info(message, additional);
    }

    public log(message: any, ...additional: any[]): void {
        this._logger.log(message, additional);
    }

    public warn(message: any, ...additional: any[]): void {
        this._logger.warn(message, additional);
    }

    public error(message: any, ...additional: any[]): void {
        this._logger.error(message, additional);
    }

    public fatal(message: any, ...additional: any[]): void {
        this._logger.fatal(message, additional);
    }
    public get level(): NgxLoggerLevel {
        return this._logger.getConfigSnapshot().level;
    }
}
