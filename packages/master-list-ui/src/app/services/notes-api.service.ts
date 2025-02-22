import { Injectable } from "@angular/core";
import { NoteElement } from "../types/note";

@Injectable({
    providedIn: 'root',
})
export class NotesApiService {
    // API calls for notes
    async getNoteElements(noteId: string): Promise<NoteElement[]> {
        // Call the API to get elements for a note
        return [];
    }
    
    async updateNoteElements(noteId: string, elements: NoteElement[]): Promise<void> {
        // Call the API to update elements for a note
    }
    
    async createNoteElement(noteId: string, element: NoteElement): Promise<void> {
        // Call the API to create a new element
    }
    
    async deleteNoteElement(noteId: string, elementId: string): Promise<void> {
        // Call the API to delete an element
    }
}