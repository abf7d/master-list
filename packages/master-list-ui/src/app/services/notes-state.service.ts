import { Injectable } from '@angular/core';
import { Note, NoteElement } from '../types/note';

@Injectable({
    providedIn: 'root',
})
export class NoteStateService {
    public notes: Map<string, Note> = new Map();
    public elements: Map<string, NoteElement> = new Map();
    
    // Cache for visible elements (for virtual scrolling)
    public visibleElements: Map<string, NoteElement> = new Map();
    
    // Queue for pending updates to avoid excessive API calls
    public updateQueue: Map<string, NoteElement> = new Map();
    public saveTimeout: any = null;
    public readonly SAVE_DELAY = 1500; // 1.5 seconds after last change
    
    // Add methods for CRUD operations
    // ...
  }