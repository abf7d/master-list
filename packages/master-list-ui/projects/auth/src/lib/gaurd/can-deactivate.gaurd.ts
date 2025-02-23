import { Inject, Injectable } from '@angular/core';
import { CanDeactivate } from '@angular/router';
import { ComponentCanDeactivate } from './component-can-deactivate';
// import { EventService, EVENT_SERVICE_TOKEN, DASHBOARD_TOKEN, DashboardService } from '@critical-pass/shared/data-access';
@Injectable()
export class CanDeactivateGuard implements CanDeactivate<ComponentCanDeactivate> {
    constructor(
        // @Inject(EVENT_SERVICE_TOKEN) private eventService: EventService,
        // @Inject(DASHBOARD_TOKEN) private dashboard: DashboardService,
    ) {}
    canDeactivate(component: ComponentCanDeactivate): boolean {
        if (!component.canDeactivate()) {
            if (confirm('You have unsaved changes! If you leave, your changes will be lost.')) {
                // this.eventService.onDestroy();
                // this.dashboard.onDestroy();
                return true;
            } else {
                return false;
            }
        }
        // this.eventService.onDestroy();
        // this.dashboard.onDestroy();
        return true;
    }
}