// modal.service.ts
import { Injectable, ApplicationRef, ComponentRef, EnvironmentInjector, createComponent, Type } from '@angular/core';
import { ConfirmDialogComponent } from './confirm-dialog.component';
import { firstValueFrom, mapTo, race } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ModalService {
    private current?: ComponentRef<any>;

    constructor(
        private appRef: ApplicationRef,
        private env: EnvironmentInjector,
    ) {}

    /** Generic opener in case you want other dialog kinds later */
    open<T extends object, R>(cmp: Type<T>, inputs: Partial<T> = {}): Promise<R | undefined> {
        // 1 – Close anything that might still be open
        this.close();

        // 2 – Create the component ***without*** boot-strapping it
        const ref = createComponent(cmp, { environmentInjector: this.env });

        // 3 – Push inputs
        Object.entries(inputs).forEach(([key, value]) => ref.setInput?.(key, value as T[keyof T]));

        // 4 – Attach to the change-detection tree **before** we append to <body>
        this.appRef.attachView(ref.hostView);

        // 5 – Physically place the host element on the page
        document.body.appendChild(ref.location.nativeElement);

        // 6 – Wire Outputs to a Promise (specific to ConfirmDialogComponent)
        this.current = ref;

        if (ref.instance instanceof ConfirmDialogComponent) {
            const ok$ = ref.instance.confirmed.pipe(mapTo(true));   // 🔑  map to TRUE
            const no$ = ref.instance.cancelled.pipe(mapTo(false));  // 🔑  map to FALSE
          
            const result$ = race(ok$, no$);             // first emission wins
          
            // Close the dialog after either click
            result$.subscribe(() => this.close());
          
            // Convert Observable<boolean> → Promise<boolean>
            return firstValueFrom(result$) as unknown as Promise<R | undefined>;;
          }

        // For non-confirm dialogs just resolve when it’s closed
        return Promise.resolve(undefined);
    }

    /** Convenience wrapper for the classic “Are you sure?” */
    confirm(
        opts: {
            title?: string;
            message?: string;
            okText?: string;
            cancelText?: string;
            maxWidth?: string;
        } = {},
    ): Promise<boolean | undefined> {
        return this.open<ConfirmDialogComponent, boolean>(ConfirmDialogComponent, opts);
    }

    /** Close & flush the current dialog, if any */
    close() {
        if (!this.current) return;
        this.appRef.detachView(this.current.hostView);
        this.current.destroy();
        this.current = undefined;
    }
}
