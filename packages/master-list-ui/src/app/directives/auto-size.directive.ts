import { Directive, ElementRef, HostListener, OnChanges, Optional, Self } from '@angular/core';
import { NgControl } from '@angular/forms';

@Directive({
  selector: 'textarea[autosize]',
  standalone: true
})
export class AutosizeDirective {
  constructor(
    private el: ElementRef<HTMLTextAreaElement>,
    @Optional() @Self() private ngControl: NgControl
  ) {}

  ngAfterViewInit() {
    // initial pass
    queueMicrotask(() => this.resize());

    // form-driven updates
    if (this.ngControl?.valueChanges) {
      this.ngControl.valueChanges.subscribe(() => this.resize());
    }
  }

  @HostListener('input') onInput() {
    this.resize();
  }

  private resize() {
    const ta = this.el.nativeElement;
    ta.style.height = 'auto';
    ta.style.height = `${ta.scrollHeight}px`;
  }
}