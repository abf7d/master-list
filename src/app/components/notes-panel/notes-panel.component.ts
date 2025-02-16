import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Note, Paragraph } from '../../types/paragraph';

@Component({
  selector: 'app-notes-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notes-panel" [class.open]="isOpen">
      <div class="notes-header">
        <h3>Notes</h3>
        <button (click)="close.emit()">Close</button>
      </div>
      <div class="notes-list">
        <div *ngFor="let note of notes" class="note-item">
          <div class="note-meta">
            <span class="note-date">{{ note.createdAt | date:'short' }}</span>
            <!-- <span class="note-paragraph">{{ getParagraphPreview(note.paragraphId) }}</span> -->
          </div>
          <div class="note-content">{{ note.content }}</div>
          <div class="note-actions">
            <button (click)="editNote.emit(note)">Edit</button>
            <button (click)="deleteNote.emit(note)">Delete</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .notes-panel {
      position: fixed;
      right: 0;
      top: 0;
      width: 300px;
      height: 100vh;
      background: #f5f5f5;
      border-left: 1px solid #ddd;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      display: flex;
      flex-direction: column;
    }

    .notes-panel.open {
      transform: translateX(0);
    }

    .notes-header {
      padding: 1rem;
      border-bottom: 1px solid #ddd;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .notes-list {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
    }

    .note-item {
      background: white;
      border-radius: 4px;
      padding: 1rem;
      margin-bottom: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .note-meta {
      font-size: 0.8rem;
      color: #666;
      margin-bottom: 0.5rem;
    }

    .note-content {
      margin-bottom: 0.5rem;
    }

    .note-actions {
      display: flex;
      gap: 0.5rem;
    }

    button {
      padding: 0.25rem 0.5rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      background: #007bff;
      color: white;
    }

    button:last-child {
      background: #dc3545;
    }
  `]
})
export class NotesPanelComponent {
  @Input() isOpen = false;
  @Input() notes: Note[] = [];
  @Input() paragraphs: Paragraph[] = [];
  
  @Output() close = new EventEmitter<void>();
  @Output() editNote = new EventEmitter<Note>();
  @Output() deleteNote = new EventEmitter<Note>();

  getParagraphPreview(paragraphId: string): string {
    const paragraph = this.paragraphs.find(p => p.id === paragraphId);
    if (!paragraph) return '';
    
    // Strip HTML and return first 30 characters
    const text = paragraph.content.replace(/<[^>]*>/g, '');
    return text.length > 30 ? text.substring(0, 30) + '...' : text;
  }
}