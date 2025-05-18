import { Injectable } from '@angular/core';
import { Paragraph } from '../types/note';

@Injectable({
  providedIn: 'root'
})
export class ListHistoryService {

  private history: Paragraph[][] = [];
  private currentIndex: number = -1;
  private isUndoRedoing: boolean = false;
  private maxHistorySize: number = 4 // Default limit
  
  constructor() {
    // Allow custom history size limit
    // if (maxHistorySize !== undefined && maxHistorySize > 0) {
    //   this.maxHistorySize = maxHistorySize;
    // }
  }
  
  get isPerformingOperation(): boolean {
    return this.isUndoRedoing;
  }
  
  // Save the current state of paragraphs
  saveState(paragraphs: Paragraph[]) {
    if (this.isUndoRedoing) return;
    
    // Create a deep copy of the paragraphs array
    const stateCopy = JSON.parse(JSON.stringify(paragraphs));
    
    // If we've undone changes and now making a new change,
    // discard any future states
    if (this.currentIndex < this.history.length - 1) {
      this.history = this.history.slice(0, this.currentIndex + 1);
    }
    
    // Add the new state
    this.history.push(stateCopy);
    this.currentIndex = this.history.length - 1;
    
    // Enforce history size limit by removing oldest entries
    if (this.history.length > this.maxHistorySize) {
      // Remove the oldest state(s)
      const excessEntries = this.history.length - this.maxHistorySize;
      this.history = this.history.slice(excessEntries);
      this.currentIndex -= excessEntries;
    }
  }
  
  // Clear all history
  clearHistory() {
    // Keep only the most recent state if available
    if (this.history.length > 0 && this.currentIndex >= 0) {
      const latestState = this.history[this.currentIndex];
      this.history = [latestState];
      this.currentIndex = 0;
    } else {
      this.history = [];
      this.currentIndex = -1;
    }
  }
  
  // Other methods remain the same
  get canUndo(): boolean {
    return this.currentIndex > 0;
  }
  
  get canRedo(): boolean {
    return this.currentIndex < this.history.length - 1;
  }
  
  undo(): Paragraph[] | null {
    if (!this.canUndo) return null;
    
    this.isUndoRedoing = true;
    this.currentIndex--;
    const state = JSON.parse(JSON.stringify(this.history[this.currentIndex]));
    this.isUndoRedoing = false;
    
    return state;
  }
  
  redo(): Paragraph[] | null {
    if (!this.canRedo) return null;
    
    this.isUndoRedoing = true;
    this.currentIndex++;
    const state = JSON.parse(JSON.stringify(this.history[this.currentIndex]));
    this.isUndoRedoing = false;
    
    return state;
  }
  
  // Get current history size
  get historySize(): number {
    return this.history.length;
  }
}
