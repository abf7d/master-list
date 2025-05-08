import { Directive, ElementRef, HostListener } from '@angular/core';

@Directive({
  selector: 'textarea[autosize]',
  standalone: true
})
export class AutosizeDirective {
  constructor(private el: ElementRef<HTMLTextAreaElement>) {}

  @HostListener('input')
  onInput(): void {
    const textarea = this.el.nativeElement;
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }

  ngAfterViewInit(): void {
    this.onInput(); // Resize on init if there's preset content
  }
}