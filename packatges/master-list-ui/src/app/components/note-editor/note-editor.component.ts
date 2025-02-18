// import { Component } from '@angular/core';

// @Component({
//   selector: 'app-note-editor',
//   imports: [],
//   templateUrl: './note-editor.component.html',
//   styleUrl: './note-editor.component.scss'
// })
// export class NoteEditorComponent {

// }


import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-note-editor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="note-editor" [class.open]="isOpen">
      <div class="note-content">
        <textarea
          [(ngModel)]="noteContent"
          placeholder="Add a note..."
          (keydown.enter)="saveNote()"
        ></textarea>
        <div class="note-actions">
          <button (click)="saveNote()">Save</button>
          <button (click)="cancel()">Cancel</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .note-editor {
      position: absolute;
      right: 300px;
      width: 300px;
      background: #f5f5f5;
      border-left: 1px solid #ddd;
      height: 100vh;
      padding: 1rem;
      transform: translateX(100%);
      transition: transform 0.3s ease;
    }

    .note-editor.open {
      transform: translateX(0);
    }

    .note-content {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    textarea {
      width: 100%;
      min-height: 100px;
      padding: 0.5rem;
      border: 1px solid #ddd;
      border-radius: 4px;
    }

    .note-actions {
      display: flex;
      gap: 0.5rem;
    }

    button {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    button:first-child {
      background: #007bff;
      color: white;
    }

    button:last-child {
      background: #6c757d;
      color: white;
    }
  `]
})
export class NoteEditorComponent {
  @Input() isOpen = false;
  @Input() initialContent = '';
  @Output() saved = new EventEmitter<string>();
  @Output() closed = new EventEmitter<void>();

  noteContent = '';

  ngOnInit() {
    this.noteContent = this.initialContent;
  }

  saveNote() {
    if (this.noteContent.trim()) {
      this.saved.emit(this.noteContent);
      this.noteContent = '';
    }
  }

  cancel() {
    this.noteContent = '';
    this.closed.emit();
  }
}