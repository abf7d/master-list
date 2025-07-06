import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy, HostListener } from '@angular/core';

@Component({
    selector: 'app-confirm-dialog',
    imports: [CommonModule],
    templateUrl: './confirm-dialog.component.html',
    styleUrl: './confirm-dialog.component.scss',
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfirmDialogComponent {
    @Input() title = 'Please confirm';
    @Input() message = 'test';
    @Input() okText = 'Confirm';
    @Input() cancelText = 'Cancel';
    @Input() maxWidth = '500px';

    @Output() confirmed = new EventEmitter<void>();
    @Output() cancelled = new EventEmitter<void>();

    ngOnInit() {
        console.log('title', this.title);
    }

    titleId = `dlg-title-${crypto.randomUUID()}`;
    msgId = `dlg-msg-${crypto.randomUUID()}`;
    hasProjectedContent = false;

    @HostListener('document:keydown.escape') onEsc() {
        this.cancel();
    }

    confirm() {
        this.confirmed.emit();
    }
    cancel() {
        this.cancelled.emit();
    }
}
