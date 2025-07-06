import { TestBed, async, inject } from '@angular/core/testing';

import { AuthorizedUserGuard } from './authorized-user.guard';

describe('AuthorizedUserGuard', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [AuthorizedUserGuard],
        });
    });

    it('should ...', inject([AuthorizedUserGuard], (guard: AuthorizedUserGuard) => {
        expect(guard).toBeTruthy();
    }));
});
