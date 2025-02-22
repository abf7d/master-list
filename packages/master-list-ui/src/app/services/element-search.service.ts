import { Injectable } from "@angular/core";

interface SearchResult {
    elementId: string;
    elementIndex: number;  // Position in the note
    startOffset: number;   // Character position in the element
    endOffset: number;     // End character position
    previewText: string;   // Context around the match
  }

@Injectable({
    providedIn: 'root',
})
export class SearchService {
    private currentNote: string | null = null;
    private searchResults: SearchResult[] = [];
    private currentResultIndex: number = -1;
    
   
    
    // // Search the current note for a query string
    // async searchNote(noteId: string, query: string): Promise<SearchResult[]> {
    //   if (!query.trim()) {
    //     this.clearSearch();
    //     return [];
    //   }
      
    //   this.currentNote = noteId;
    //   const note = await this.noteService.getNote(noteId);
      
    //   // For virtual scrolling optimization, we might need to fetch all elements
    //   // This could be done incrementally or in a background worker for large notes
    //   const elements = await this.noteService.getAllElements(noteId);
      
    //   // Perform the search
    //   this.searchResults = [];
    //   const lowerQuery = query.toLowerCase();
      
    //   elements.forEach((element, index) => {
    //     const lowerContent = element.content.toLowerCase();
    //     let position = 0;
        
    //     // Find all instances of the query in this element
    //     while (position < lowerContent.length) {
    //       const foundPos = lowerContent.indexOf(lowerQuery, position);
    //       if (foundPos === -1) break;
          
    //       // Create a result with context
    //       const startPreview = Math.max(0, foundPos - 20);
    //       const endPreview = Math.min(element.content.length, foundPos + query.length + 20);
          
    //       this.searchResults.push({
    //         elementId: element.id,
    //         elementIndex: index,
    //         startOffset: foundPos,
    //         endOffset: foundPos + query.length,
    //         previewText: '...' + element.content.substring(startPreview, endPreview) + '...'
    //       });
          
    //       position = foundPos + query.length;
    //     }
    //   });
      
    //   // Reset the result navigation
    //   this.currentResultIndex = this.searchResults.length > 0 ? 0 : -1;
      
    //   return this.searchResults;
    // }
    
    // // Navigate to the next search result
    // nextResult(): SearchResult | null {
    //   if (this.searchResults.length === 0) return null;
      
    //   this.currentResultIndex = (this.currentResultIndex + 1) % this.searchResults.length;
    //   return this.navigateToResult(this.currentResultIndex);
    // }
    
    // // Navigate to the previous search result
    // previousResult(): SearchResult | null {
    //   if (this.searchResults.length === 0) return null;
      
    //   this.currentResultIndex = (this.currentResultIndex - 1 + this.searchResults.length) % this.searchResults.length;
    //   return this.navigateToResult(this.currentResultIndex);
    // }
    
    // // Scroll to a specific search result
    // navigateToResult(index: number): SearchResult | null {
    //   if (index < 0 || index >= this.searchResults.length) return null;
      
    //   const result = this.searchResults[index];
      
    //   // Tell the virtual scroller to scroll to this element
    //   this.virtualScrollService.scrollToIndex(result.elementIndex);
      
    //   // Highlight the text within the element (implementation depends on your editor)
    //   this.highlightService.highlightText(result.elementId, result.startOffset, result.endOffset);
      
    //   return result;
    // }
    
    // // Clear search results
    // clearSearch(): void {
    //   this.searchResults = [];
    //   this.currentResultIndex = -1;
    //   this.currentNote = null;
    //   this.highlightService.clearHighlights();
    // }
  }