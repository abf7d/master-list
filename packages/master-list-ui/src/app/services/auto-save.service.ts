import { Injectable } from "@angular/core";
import { NoteElement } from "../types/note";
import { NoteStateService } from "./notes-state.service";
import { NotesApiService } from "./notes-api.service";

@Injectable({
    providedIn: 'root',
})
export class AutoSaveService {
    constructor(private notesApi: NotesApiService) {}
 // Auto-save implementation
 queueElementForSave(element: NoteElement, state: NoteStateService): void {
    // Mark element as modified
    element.isModified = true;
    element.timestamp = Date.now();
    
    // Add to update queue, overwriting previous version if exists
    state.updateQueue.set(element.id, element);
    
    // Reset timer
    if (state.saveTimeout) {
      clearTimeout(state.saveTimeout);
    }
    
    // Start new timer
    state.saveTimeout = setTimeout(() => {
      this.saveQueuedElements(state);
    }, state.SAVE_DELAY);
  }
  
  // Save queued elements to backend
  async saveQueuedElements(state: NoteStateService, retryCount = 1): Promise<void> {
    if (state.updateQueue.size === 0) return;
    
    // Create a copy of the current queue
    const elementsToSave = new Map(state.updateQueue);
    // Clear the queue
    state.updateQueue.clear();
    
    try {
      // Convert to array for API call
      const elementsArray = Array.from(elementsToSave.values());
      
      // Group by note ID for more efficient API calls
      const elementsByNote = this.groupBy(elementsArray, 'noteId');
      
      // Save each group
      for (const [noteId, elements] of Object.entries(elementsByNote)) {
        await this.notesApi.updateNoteElements(noteId, elements);
        
        // Update last modified timestamp for the note
        const note = state.notes.get(noteId);
        if (note) {
          note.lastModified = Date.now();
          state.notes.set(noteId, note);
        }
      }
      
      // Mark elements as saved
      elementsArray.forEach(element => {
        element.isModified = false;
        state.elements.set(element.id, element);
      });
      
      // Notify success
    //   notificationService.showSuccess('Changes saved successfully');
    } catch (error) {
      // Put elements back in the queue
      elementsToSave.forEach((element, id) => {
        state.updateQueue.set(id, element);
      });
      
      // Schedule retry with exponential backoff
      const backoffTime = this.calculateBackoffTime(retryCount++);
      setTimeout(() => {
        this.saveQueuedElements(state, retryCount);
      }, backoffTime);
      
      // Notify error
    //   notificationService.showError('Failed to save changes. Retrying...');
    }
  }

  calculateBackoffTime(retryCount: number): number {
    // Exponential backoff with jitter
    const baseTime = 1000; // 1 second
    const maxTime = 60000; // 1 minute
    const backoffTime = Math.min(baseTime * 2 ** retryCount, maxTime);
    const jitter = Math.random() * 1000; // Random number between 0 and 1 second
    return backoffTime + jitter;
  }
  
  // Helper function to group elements by note ID
  groupBy(array: any[], key: string): Record<string, any[]> {
    return array.reduce((result, item) => {
      (result[item[key]] = result[item[key]] || []).push(item);
      return result;
    }, {});
  }
}