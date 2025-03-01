import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  HostListener,
  ViewChild,
  ViewEncapsulation,
} from '@angular/core';
import { ParagraphNote, Paragraph } from '../../types/note'
import { MetaTagService } from '../meta-tags/meta-tag.service';
import { MetaTagsComponent } from '../meta-tags/meta-tags.component';
import { NotesApiService } from '../../services/notes-api.service';
// import { NoteEditorComponent } from '../note-editor/note-editor.component';
// import { NotesPanelComponent } from '../notes-panel/notes-panel.component';

@Component({
  selector: 'app-master-layout',
  imports: [
    CommonModule,
    MetaTagsComponent
    // NoteEditorComponent,
    // NotesPanelComponent
  ],
  templateUrl: './master-layout.component.html',
  styleUrl: './master-layout.component.scss',
  encapsulation: ViewEncapsulation.None
})


// BREAKPOINT 2!!!!
export class MasterLayoutComponent implements AfterViewInit {
  @ViewChild('editor') editorRef!: ElementRef;

  paragraphs: Paragraph[] = [];
  selectedParagraphId: string | null = null;
  selectedParagraphIds: string[] = [];
  selectedTab = 'tags';

  affectedRows: any[] = [];
  constructor(private notesApi: NotesApiService) {}

  applyInlineStyle(style: string): void {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;
  
    const range = selection.getRangeAt(0);
  
    // Get start and end nodes
    let startNode = range.startContainer;
    let endNode = range.endContainer;
  
    // Find the containing content divs and editor rows
    let startContentDiv = this.findParentWithClass(startNode, 'content-div');
    let endContentDiv = this.findParentWithClass(endNode, 'content-div');
    
    if (!startContentDiv || !endContentDiv) return;
    
    // Find the editor rows that contain these content divs
    let startEditorRow = this.findParentWithClass(startContentDiv, 'editor-row');
    let endEditorRow = this.findParentWithClass(endContentDiv, 'editor-row');
    
    if (!startEditorRow || !endEditorRow) return;
  
    // Create the style span
    const span = document.createElement('span');
    switch (style) {
      case 'bold':
        span.style.fontWeight = 'bold';
        break;
      case 'italic':
        span.style.fontStyle = 'italic';
        break;
      case 'large':
        span.style.fontSize = '1.2em';
        break;
    }
  
    // Handle single editor row case
    if (startEditorRow === endEditorRow) {
      const content = range.extractContents();
      span.appendChild(content);
      range.insertNode(span);
    }
    // Handle multiple editor rows
    else {
      // Get all affected editor rows
      const affectedRows = this.getElementsBetween(startEditorRow, endEditorRow);
  
      affectedRows.forEach((row, index) => {
        // Find the content div within this row
        const contentDiv = row.querySelector('.content-div');
        if (!contentDiv) return;
        
        const contentRange = document.createRange();
        contentRange.selectNodeContents(contentDiv);
  
        // For first row, start from selection start
        if (index === 0) {
          contentRange.setStart(range.startContainer, range.startOffset);
        }
  
        // For last row, end at selection end
        if (index === affectedRows.length - 1) {
          contentRange.setEnd(range.endContainer, range.endOffset);
        }
  
        // Apply styling to the range
        const clonedSpan = span.cloneNode() as HTMLElement;
        const content = contentRange.extractContents();
        clonedSpan.appendChild(content);
        contentRange.insertNode(clonedSpan);
      });
      this.setAffectedElements(affectedRows);
    }
    
    // Update our data model
    this.updateParagraphContent();
  
    // Restore selection
    selection.removeAllRanges();
    selection.addRange(range);
  }

  // When a tag or tags are assigned, use applyInlineStyle function that uses this function
  // to aggregate selected paragraphs. Either use affectedRows or then selectedParagraphs (background yellow)
  // to associate tag then add class name to bullet points for color and dynamically set color with css variables
  private setAffectedElements(affectedRows: any[]) {
    const ids = new Map<string, boolean>(affectedRows.map(x => [x.id, true]));
    this.affectedRows = this.paragraphs.filter(x => {
      return ids.get(x.id);
    })
    console.log(this.affectedRows);
  }
  
  // Helper method to find parent element with a specific class
  private findParentWithClass(node: Node, className: string): HTMLElement | null {
    let current = node;
    
    // If it's a text node, start with its parent
    if (current.nodeType === Node.TEXT_NODE) {
      current = current.parentElement!;
    }
    
    // Traverse up the DOM tree looking for an element with the specified class
    while (current && current instanceof HTMLElement) {
      if (current.classList.contains(className)) {
        return current;
      }
      current = current.parentElement!;
    }
    
    return null;
  }
  
  // Helper method to get all editor rows between two elements
  private getElementsBetween(
    startElement: HTMLElement,
    endElement: HTMLElement
  ): HTMLElement[] {
    const elements: HTMLElement[] = [];
    let currentElement: HTMLElement | null = startElement;
  
    while (currentElement) {
      elements.push(currentElement);
  
      if (currentElement === endElement) break;
  
      // Get next editor row
      currentElement = currentElement.nextElementSibling as HTMLElement;
      if (!currentElement || !currentElement.classList.contains('editor-row')) break;
    }
  
    return elements;
  }

  // applyInlineStyle(style: string): void {
  //   const selection = window.getSelection();
  //   if (!selection || selection.rangeCount === 0) return;

  //   const range = selection.getRangeAt(0);

  //   // Get start and end paragraphs
  //   let startNode = range.startContainer;
  //   let endNode = range.endContainer;

  //   // Find the containing paragraphs
  //   let startParagraph =
  //     startNode.nodeType === Node.TEXT_NODE
  //       ? (startNode.parentElement as HTMLElement)?.closest('p')
  //       : (startNode as HTMLElement).closest('p');
  //   let endParagraph =
  //     endNode.nodeType === Node.TEXT_NODE
  //       ? (endNode.parentElement as HTMLElement)?.closest('p')
  //       : (endNode as HTMLElement).closest('p');

  //   if (!startParagraph || !endParagraph) return;

  //   // Create the style span
  //   const span = document.createElement('span');
  //   switch (style) {
  //     case 'bold':
  //       span.style.fontWeight = 'bold';
  //       break;
  //     case 'italic':
  //       span.style.fontStyle = 'italic';
  //       break;
  //     case 'large':
  //       span.style.fontSize = '1.2em';
  //       break;
  //   }

  //   // Handle single paragraph case
  //   if (startParagraph === endParagraph) {
  //     const content = range.extractContents();
  //     span.appendChild(content);
  //     range.insertNode(span);
  //   }
  //   // Handle multiple paragraphs
  //   else {
  //     // Create ranges for each affected paragraph
  //     const affectedParagraphs = this.getElementsBetween(
  //       startParagraph,
  //       endParagraph
  //     );

  //     affectedParagraphs.forEach((paragraph, index) => {
  //       const paragraphRange = document.createRange();
  //       paragraphRange.selectNodeContents(paragraph);

  //       // For first paragraph, start from selection start
  //       if (index === 0) {
  //         paragraphRange.setStart(range.startContainer, range.startOffset);
  //       }

  //       // For last paragraph, end at selection end
  //       if (index === affectedParagraphs.length - 1) {
  //         paragraphRange.setEnd(range.endContainer, range.endOffset);
  //       }

  //       // Apply styling to the range
  //       const clonedSpan = span.cloneNode() as HTMLElement;
  //       const content = paragraphRange.extractContents();
  //       clonedSpan.appendChild(content);
  //       paragraphRange.insertNode(clonedSpan);
  //     });
  //   }
  //   // Update our data model
  //   this.updateParagraphContent();

  //   // Restore selection
  //   selection.removeAllRanges();
  //   selection.addRange(range);
  // }

  // // Helper method to get all paragraphs between two elements
  // private getElementsBetween(
  //   startElement: HTMLElement,
  //   endElement: HTMLElement
  // ): HTMLElement[] {
  //   const elements: HTMLElement[] = [];
  //   let currentElement: HTMLElement | null = startElement;

  //   while (currentElement) {
  //     elements.push(currentElement);

  //     if (currentElement === endElement) break;

  //     // Get next paragraph
  //     currentElement = currentElement.nextElementSibling as HTMLElement;
  //     if (!currentElement || !currentElement.matches('p')) break;
  //   }

  //   return elements;
  // }

  // Update the updateParagraphContent method to work with the new structure
private updateParagraphContent(): void {
  const rowElements = this.editorRef.nativeElement.querySelectorAll('.editor-row');

  this.paragraphs = Array.from(rowElements).map((row: any) => {
    const contentDiv = row.querySelector('.content-div');
    const existingParagraph = this.paragraphs.find(
      (para) => para.id === row.id
    );
    
    return {
      id: row.id,
      content: contentDiv.innerHTML,
      styles: existingParagraph?.styles || {
        fontSize: '16px',
        textAlign: 'left',
      },
      type: existingParagraph?.type || 'none',
      level: existingParagraph?.level || 0,
      notes: existingParagraph?.notes || []
    };
  });
}
  // private updateParagraphContent(): void {
  //   const paragraphElements =
  //     this.editorRef.nativeElement.getElementsByTagName('p');

  //   this.paragraphs = Array.from(paragraphElements).map((p: any) => {
  //     const existingParagraph = this.paragraphs.find(
  //       (para) => para.id === p.id
  //     );
  //     return {
  //       id: p.id,
  //       content: p.innerHTML,
  //       styles: existingParagraph?.styles || {
  //         fontSize: '16px',
  //         textAlign: 'left',
  //       },
  //       type: existingParagraph?.type || 'none',
  //       level: existingParagraph?.level || 0,
  //       notes: existingParagraph?.notes || []
  //     };
  //   });
  // }


  ngAfterViewInit() {
    if (!this.paragraphs.length) {
      this.createNewParagraph();
    }
    this.renderParagraphs();

    // Set focus to the first paragraph
    const firstP = this.editorRef.nativeElement.querySelector('p');
    if (firstP) {
      const range = document.createRange();
      range.setStart(firstP, 0);
      range.collapse(true);
      const selection = window.getSelection();
      if (selection) {
        selection.removeAllRanges();
        selection.addRange(range);
      }
    }
  }

  private createNewParagraph(content: string = '', level: number = 0): void {
    const paragraph: Paragraph = {
      id: crypto.randomUUID(),
      content: content,
      styles: {
        fontSize: '16px',
        textAlign: 'left',
        minHeight: '24px',
      },
      type: 'none',
      level: level,
      notes: []
    };
  
    this.paragraphs.push(paragraph);
    this.renderParagraphs();
  }
  // private createNewParagraph(content: string = '', level: number = 0): void {
  //   const paragraph: Paragraph = {
  //     id: crypto.randomUUID(),
  //     content: content,
  //     styles: {
  //       fontSize: '16px',
  //       textAlign: 'left',
  //       minHeight: '24px',
  //     },
  //     type: 'none',
  //     level: level,
  //     notes: []
  //   };

  //   this.paragraphs.push(paragraph);
  //   this.renderParagraphs();
  // }

  
// Modify the renderParagraphs method to use nested divs instead of paragraphs
private renderParagraphs(): void {
  const editor = this.editorRef.nativeElement;
  editor.innerHTML = '';

  // Define bullet styles - you can customize these colors
  const bulletColors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12'];

  this.paragraphs.forEach((paragraph, i: number) => {
    // Create the outermost div (replaces the p element)
    const outerDiv = document.createElement('div');
    outerDiv.className = 'editor-row';
    outerDiv.id = paragraph.id;
    
    // Create nested structure with 4 levels of divs for bullets
    const level3 = document.createElement('div');
    level3.className = 'bullet';
    
    const level2 = document.createElement('div');
    level2.className = 'bullet';
    level3.appendChild(level2);
    
    const level1 = document.createElement('div');
    level1.className = 'bullet';
    level2.appendChild(level1);
    
    // This is the innermost div that will contain the actual content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'bullet content-div';
    contentDiv.setAttribute('contenteditable', 'true');
    contentDiv.innerHTML = paragraph.content;
    level1.appendChild(contentDiv);
    
    // Apply styles from paragraph to the content div
    Object.assign(contentDiv.style, paragraph.styles);
    
    // Handle indentation
    outerDiv.style.paddingLeft = `${paragraph.level * 40}px`;
    
    // Add the nested structure to the editor
    outerDiv.appendChild(level3);
    editor.appendChild(outerDiv);
    
    // Mark this row with its type if it's a list item
    if (paragraph.type === 'number' || paragraph.type === 'bullet') {
      outerDiv.setAttribute('data-list-type', paragraph.type);
    }
  });
}
  
  // // Modify the renderParagraphs method to handle numbered lists properly
  // private renderParagraphs(): void {
  //   const editor = this.editorRef.nativeElement;
  //   editor.innerHTML = '';

  //   // Keep track of numbering at each level
  //   const numberingByLevel: { [key: number]: number } = {};

  //   this.paragraphs.forEach((paragraph, i: number) => {
  //     const p = document.createElement('p');
  //     p.innerHTML = paragraph.content;
  //     p.id = paragraph.id;

  //     // const styles = { ...paragraph.styles, gridRow: i + 1, gridColumn: 2 }; 
  //     // Object.assign(p.style, styles);

  //     Object.assign(p.style, paragraph.styles);
  //     p.style.paddingLeft = `${paragraph.level * 40}px`;

  //     // Reset numbering when type changes or there's a gap in numbering
  //     if (paragraph.type === 'number') {
  //       // Initialize counter for this level if it doesn't exist
  //       if (!numberingByLevel[paragraph.level]) {
  //         numberingByLevel[paragraph.level] = 1;
  //       }
  //     }

  //     editor.appendChild(p);

  //     // Increment counter for numbered lists
  //     if (paragraph.type === 'number') {
  //       numberingByLevel[paragraph.level]++;
  //     }
  //   });
  // }

  
  ctrlDown = false;
  @HostListener('keydown.meta', ['$event'])
  onMeta(event: KeyboardEvent): void {
    this.ctrlDown = true;
  }
  @HostListener('keyup.meta', ['$event'])
  offMeta(event: KeyboardEvent): void {
    this.ctrlDown = false;
  }
  @HostListener('keydown.ctrl', ['$event'])
  onCtrl(event: KeyboardEvent): void {
    this.ctrlDown = true;
  }
  @HostListener('keyup.ctrl', ['$event'])
  offCtrl(event: KeyboardEvent): void {
    this.ctrlDown = false;
  }


  onInput(event: Event): void {
    const editor = this.editorRef.nativeElement;
  
    // Handle direct text nodes
    const childNodes = Array.from(editor.childNodes);
    childNodes.forEach((node: any) => {
      if (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) {
        // Create the nested div structure
        const outerDiv = document.createElement('div');
        outerDiv.className = 'editor-row';
        outerDiv.id = crypto.randomUUID();
        
        const level3 = document.createElement('div');
        level3.className = 'bullet';
        
        const level2 = document.createElement('div');
        level2.className = 'bullet';
        level3.appendChild(level2);
        
        const level1 = document.createElement('div');
        level1.className = 'bullet';
        level2.appendChild(level1);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'bullet content-div';
        contentDiv.setAttribute('contenteditable', 'true');
        contentDiv.textContent = node.textContent;
        level1.appendChild(contentDiv);
        
        // Remove the text node and add our structure
        node.parentNode?.removeChild(node);
        outerDiv.appendChild(level3);
        editor.insertBefore(outerDiv, editor.firstChild);
  
        // Add to our data model
        this.paragraphs.unshift({
          id: outerDiv.id,
          content: contentDiv.innerHTML,
          styles: {
            fontSize: '16px',
            textAlign: 'left',
            minHeight: '24px',
          },
          type: 'none',
          level: 0,
          notes: []
        });
      }
    });
  
    this.updateParagraphContent();
  }
  // onInput(event: Event): void {
  //   const editor = this.editorRef.nativeElement;

  //   // Handle direct text nodes
  //   const childNodes = Array.from(editor.childNodes);
  //   childNodes.forEach((node: any) => {
  //     if (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) {
  //       const newP = document.createElement('p');
  //       newP.id = crypto.randomUUID();
  //       node.parentNode?.removeChild(node);
  //       newP.appendChild(node);
  //       editor.insertBefore(newP, editor.firstChild);

  //       this.paragraphs.unshift({
  //         id: newP.id,
  //         content: newP.innerHTML,
  //         styles: {
  //           fontSize: '16px',
  //           textAlign: 'left',
  //           minHeight: '24px',
  //         },
  //         type: 'none',
  //         level: 0,
  //         notes: []
  //       });
  //     }
  //   });

  //   this.updateParagraphContent();
  // }


  @HostListener('keydown', ['$event'])
onKeyDown(event: KeyboardEvent): void {
  if (event.key === 'Enter') {
    event.preventDefault();

    const selection = window.getSelection();
    if (!selection) return;

    const range = selection.getRangeAt(0);
    let currentNode = range.commonAncestorContainer;

    // Find the containing editor row
    let editorRow = null;
    let node = currentNode;
    while (node && !editorRow) {
      if (node.nodeType === Node.ELEMENT_NODE && 
          (node as HTMLElement).classList.contains('editor-row')) {
        editorRow = node;
        break;
      }
      node = node.parentNode!;
    }

    if (!editorRow) return;
    const currentParagraph = editorRow as HTMLElement;

    const currentIndex = this.paragraphs.findIndex(
      (p) => p.id === currentParagraph.id
    );
    if (currentIndex === -1) return;

    // Get content from the content div
    const contentDiv = currentParagraph.querySelector('.content-div');
    const currentContent = contentDiv ? contentDiv.innerHTML : '';
    
    // Check if we're at the end of an empty paragraph
    const isEmptyParagraph =
      currentContent.trim() === '' || currentContent === '<br>';

    // If it's an empty list item, convert it to a regular paragraph
    if (isEmptyParagraph && this.paragraphs[currentIndex].type !== 'none') {
      this.paragraphs[currentIndex].type = 'none';
      this.paragraphs[currentIndex].level = 0;
      this.renderParagraphs();
      return;
    }

    // Create new paragraph with same properties
    const newParagraph: Paragraph = {
      id: crypto.randomUUID(),
      content: '<br>', // Start with empty content
      styles: { ...this.paragraphs[currentIndex].styles },
      type: this.paragraphs[currentIndex].type, // Maintain the list type
      level: this.paragraphs[currentIndex].level, // Maintain the indentation level
      notes: this.paragraphs[currentIndex].notes
    };

    // Insert new paragraph
    this.paragraphs.splice(currentIndex + 1, 0, newParagraph);
    this.renderParagraphs();

    this.selectedParagraphId = newParagraph.id;
    
    // Set cursor position to new paragraph's content div
    setTimeout(() => {
      const newElement = document.getElementById(newParagraph.id);
      if (newElement) {
        const contentDiv = newElement.querySelector('.content-div');
        if (contentDiv) {
          const range = document.createRange();
          range.setStart(contentDiv, 0);
          range.collapse(true);

          const selection = window.getSelection();
          if (selection) {
            selection.removeAllRanges();
            selection.addRange(range);
          }
        }
      }
    }, 0);
  }
}
  // @HostListener('keydown', ['$event'])
  // onKeyDown(event: KeyboardEvent): void {
  //   if (event.key === 'Enter') {
  //     event.preventDefault();

  //     const selection = window.getSelection();
  //     if (!selection) return;

  //     const range = selection.getRangeAt(0);
  //     let currentNode = range.commonAncestorContainer;

  //     // Find the containing paragraph
  //     while (
  //       currentNode &&
  //       currentNode.nodeName !== 'P' &&
  //       currentNode.parentNode
  //     ) {
  //       currentNode = currentNode.parentNode;
  //     }

  //     if (!currentNode) return;
  //     const currentParagraph = currentNode as HTMLElement;

  //     const currentIndex = this.paragraphs.findIndex(
  //       (p) => p.id === currentParagraph.id
  //     );
  //     if (currentIndex === -1) return;

  //     const currentContent = currentParagraph.innerHTML;
  //     const cursorPosition = range.startOffset;

  //     // Check if we're at the end of an empty paragraph
  //     const isEmptyParagraph =
  //       currentContent.trim() === '' || currentContent === '<br>';

  //     // If it's an empty list item, convert it to a regular paragraph
  //     if (isEmptyParagraph && this.paragraphs[currentIndex].type !== 'none') {
  //       this.paragraphs[currentIndex].type = 'none';
  //       this.paragraphs[currentIndex].level = 0;
  //       this.renderParagraphs();
  //       return;
  //     }

  //     // Create new paragraph with same list properties
  //     const newParagraph: Paragraph = {
  //       id: crypto.randomUUID(),
  //       content: '<br>', // Start with empty content
  //       styles: { ...this.paragraphs[currentIndex].styles },
  //       type: this.paragraphs[currentIndex].type, // Maintain the list type
  //       level: this.paragraphs[currentIndex].level, // Maintain the indentation level
  //       notes: this.paragraphs[currentIndex].notes
  //     };

  //     // Insert new paragraph
  //     this.paragraphs.splice(currentIndex + 1, 0, newParagraph);
  //     this.renderParagraphs();

  //     this.selectedParagraphId = newParagraph.id;
      

  //     // Set cursor position to new paragraph
  //     setTimeout(() => {
  //       const newElement = document.getElementById(newParagraph.id);
  //       if (newElement) {
  //         const range = document.createRange();
  //         range.setStart(newElement, 0);
  //         range.collapse(true);

  //         const selection = window.getSelection();
  //         if (selection) {
  //           selection.removeAllRanges();
  //           selection.addRange(range);
  //         }
  //       }
  //     }, 0);
  //   }
  // }


  // onEditorClick(event: MouseEvent): void {
  //   const target = event.target as HTMLElement;
  //   if (target.tagName === 'P') {
  //     this.selectParagraph(target.id);
  //   }
  // }

  onEditorClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    let editorRow = target.closest('.editor-row');
    
    if (editorRow) {
      this.selectParagraph(editorRow.id);
    }
  }

  selectParagraph(id: string): void {
    this.selectedParagraphId = id;
    if (this.ctrlDown) {
      if (this.selectedParagraphIds?.includes(id)) {
        this.selectedParagraphIds = this.selectedParagraphIds?.filter(
          (pId) => pId !== id
        );
      } else {
        this.selectedParagraphIds?.push(id);
      }
    }
    else {
      this.selectedParagraphIds = [id];
    }
  
    this.editorRef.nativeElement
      .querySelectorAll('.editor-row')
      .forEach((row: HTMLElement) => {
        row.classList.remove('selected');
      });
  
    const selectedElement = document.getElementById(id);
    if (selectedElement) {
      selectedElement.classList.add('selected');
    }
    
    if (this.selectedParagraphIds.length > 0) {
      this.paragraphs.forEach((p) => {
        const rowEl = document.getElementById(p.id);
        if (this.selectedParagraphIds?.includes(p.id)) {
          if (rowEl) {
            rowEl.classList.add('grouped');
          }
        } else {
          if (rowEl) {
            rowEl.classList.remove('grouped');
          }
        }
      });
    }
  }
  // selectParagraph(id: string): void {
  //   this.selectedParagraphId = id;
  //   if (this.ctrlDown) {
  //     if (this.selectedParagraphIds?.includes(id)) {
  //       this.selectedParagraphIds = this.selectedParagraphIds?.filter(
  //         (pId) => pId !== id
  //       );
  //     } else {
  //       this.selectedParagraphIds?.push(id);
  //     }
  //   }
  //   else {
  //     this.selectedParagraphIds = [id];
  //   }

  //   this.editorRef.nativeElement
  //     .querySelectorAll('p')
  //     .forEach((p: HTMLElement) => {
  //       p.classList.remove('selected');
  //     });

  //   const selectedElement = document.getElementById(id);
  //   if (selectedElement) {
  //     selectedElement.classList.add('selected');
  //   }
  //   if (this.selectedParagraphIds.length > 0) {
  //     this.paragraphs.forEach((p) => {
  //       const pEl = document.getElementById(p.id);
  //       if (this.selectedParagraphIds?.includes(p.id)) {
         
  //         if (pEl) {
  //           pEl.classList.add('grouped');
  //         }
  //       } else {
  //         if (pEl) {
  //           pEl.classList.remove('grouped');
  //         }
  //       }

  //     });
  //   }
  // }

 


  showNoteEditor = false;
  editingNote: ParagraphNote | null = null;

  handlePaste(event: ClipboardEvent) {
    // Prevent default paste behavior
    event.preventDefault();
    
    // Get the pasted text content
    const pastedText = event.clipboardData?.getData('text') || '';
    
    // Split the text by newline characters
    // This handles different types of line breaks (\n, \r\n, \r)
    const lines = pastedText.split(/\r?\n/)
      .filter(line => line.trim().length > 0); // Remove empty lines


      
    let currentIndex = this.paragraphs.length - 1;
    if (this.selectedParagraphId) {
      currentIndex = this.paragraphs.findIndex(p => p.id === this.selectedParagraphId);
    }
    // Create new notes for each line
    lines.forEach((line, i) => {
      const newParagraph: Paragraph = {
        id: crypto.randomUUID(),
        content: line, // Start with empty content
        styles: { ...this.paragraphs[currentIndex + i].styles },
        type: this.paragraphs[currentIndex + i].type, // Maintain the list type
        level: this.paragraphs[currentIndex + i].level, // Maintain the indentation level
        notes: this.paragraphs[currentIndex + i].notes
      };

      // Insert new paragraph
      this.paragraphs.splice(currentIndex + i, 0, newParagraph);
      
    });
    this.renderParagraphs();
    // Clear the paste area
    if (event.target instanceof HTMLElement) {
      event.target.textContent = '';
    }
  }
  getTags(): void {
    this.notesApi.getNoteElements('temp').subscribe((elements) => {
      console.log(elements);
    });
  }
}

//Aaron
