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


  applyInlineStyle(style: string): void {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);

    // Get start and end paragraphs
    let startNode = range.startContainer;
    let endNode = range.endContainer;

    // Find the containing paragraphs
    let startParagraph =
      startNode.nodeType === Node.TEXT_NODE
        ? (startNode.parentElement as HTMLElement)?.closest('p')
        : (startNode as HTMLElement).closest('p');
    let endParagraph =
      endNode.nodeType === Node.TEXT_NODE
        ? (endNode.parentElement as HTMLElement)?.closest('p')
        : (endNode as HTMLElement).closest('p');

    if (!startParagraph || !endParagraph) return;

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

    // Handle single paragraph case
    if (startParagraph === endParagraph) {
      const content = range.extractContents();
      span.appendChild(content);
      range.insertNode(span);
    }
    // Handle multiple paragraphs
    else {
      // Create ranges for each affected paragraph
      const affectedParagraphs = this.getElementsBetween(
        startParagraph,
        endParagraph
      );

      affectedParagraphs.forEach((paragraph, index) => {
        const paragraphRange = document.createRange();
        paragraphRange.selectNodeContents(paragraph);

        // For first paragraph, start from selection start
        if (index === 0) {
          paragraphRange.setStart(range.startContainer, range.startOffset);
        }

        // For last paragraph, end at selection end
        if (index === affectedParagraphs.length - 1) {
          paragraphRange.setEnd(range.endContainer, range.endOffset);
        }

        // Apply styling to the range
        const clonedSpan = span.cloneNode() as HTMLElement;
        const content = paragraphRange.extractContents();
        clonedSpan.appendChild(content);
        paragraphRange.insertNode(clonedSpan);
      });
    }
    // Update our data model
    this.updateParagraphContent();

    // Restore selection
    selection.removeAllRanges();
    selection.addRange(range);
  }

  // Helper method to get all paragraphs between two elements
  private getElementsBetween(
    startElement: HTMLElement,
    endElement: HTMLElement
  ): HTMLElement[] {
    const elements: HTMLElement[] = [];
    let currentElement: HTMLElement | null = startElement;

    while (currentElement) {
      elements.push(currentElement);

      if (currentElement === endElement) break;

      // Get next paragraph
      currentElement = currentElement.nextElementSibling as HTMLElement;
      if (!currentElement || !currentElement.matches('p')) break;
    }

    return elements;
  }

  private updateParagraphContent(): void {
    const paragraphElements =
      this.editorRef.nativeElement.getElementsByTagName('p');

    this.paragraphs = Array.from(paragraphElements).map((p: any) => {
      const existingParagraph = this.paragraphs.find(
        (para) => para.id === p.id
      );
      return {
        id: p.id,
        content: p.innerHTML,
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

  // Add this method to handle paragraph numbering
  getNumberForParagraph(paragraph: Paragraph, index: number): number {
    if (paragraph.type !== 'number') return 0;

    let number = 1;
    // Count previous paragraphs at the same level
    for (let i = 0; i < index; i++) {
      if (
        this.paragraphs[i].type === 'number' &&
        this.paragraphs[i].level === paragraph.level
      ) {
        number++;
      }
    }
    return number;
  }

  // ngAfterViewInit() {
  //   this.createNewParagraph();
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

  

  // Modify the renderParagraphs method to handle numbered lists properly
  private renderParagraphs(): void {
    const editor = this.editorRef.nativeElement;
    editor.innerHTML = '';

    // Keep track of numbering at each level
    const numberingByLevel: { [key: number]: number } = {};

    this.paragraphs.forEach((paragraph, i: number) => {
      const p = document.createElement('p');
      p.innerHTML = paragraph.content;
      p.id = paragraph.id;

      // const styles = { ...paragraph.styles, gridRow: i + 1, gridColumn: 2 }; 
      // Object.assign(p.style, styles);

      Object.assign(p.style, paragraph.styles);
      p.style.paddingLeft = `${paragraph.level * 40}px`;

      // Reset numbering when type changes or there's a gap in numbering
      if (paragraph.type === 'number') {
        // Initialize counter for this level if it doesn't exist
        if (!numberingByLevel[paragraph.level]) {
          numberingByLevel[paragraph.level] = 1;
        }
      }

      editor.appendChild(p);

      // Increment counter for numbered lists
      if (paragraph.type === 'number') {
        numberingByLevel[paragraph.level]++;
      }
    });
  }

  getNestedNumber(index: number): string {
    const paragraph = this.paragraphs[index];
    if (paragraph.type !== 'number') return '';

    let number = 1;
    // Count paragraphs at the same level that come before this one
    for (let i = 0; i < index; i++) {
      const prev = this.paragraphs[i];
      if (prev.type === 'number' && prev.level === paragraph.level) {
        number++;
      }
    }
    return number.toString();
  }

  changeLevel(delta: number): void {
    if (!this.selectedParagraphId) return;

    const paragraph = this.paragraphs.find(
      (p) => p.id === this.selectedParagraphId
    );
    if (paragraph) {
      // Prevent negative levels and limit max level to 5
      const newLevel = Math.max(0, Math.min(5, paragraph.level + delta));
      paragraph.level = newLevel;
      this.renderParagraphs();

      const p = document.getElementById(this.selectedParagraphId);
      if (p) {
        p.classList.add('selected');
      }
    }
  }

  @HostListener('keydown.tab', ['$event'])
  onTab(event: KeyboardEvent): void {
    event.preventDefault();
    if (event.shiftKey) {
      this.changeLevel(-1);
    } else {
      this.changeLevel(1);
    }
  }
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
        const newP = document.createElement('p');
        newP.id = crypto.randomUUID();
        node.parentNode?.removeChild(node);
        newP.appendChild(node);
        editor.insertBefore(newP, editor.firstChild);

        this.paragraphs.unshift({
          id: newP.id,
          content: newP.innerHTML,
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


  @HostListener('keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      event.preventDefault();

      const selection = window.getSelection();
      if (!selection) return;

      const range = selection.getRangeAt(0);
      let currentNode = range.commonAncestorContainer;

      // Find the containing paragraph
      while (
        currentNode &&
        currentNode.nodeName !== 'P' &&
        currentNode.parentNode
      ) {
        currentNode = currentNode.parentNode;
      }

      if (!currentNode) return;
      const currentParagraph = currentNode as HTMLElement;

      const currentIndex = this.paragraphs.findIndex(
        (p) => p.id === currentParagraph.id
      );
      if (currentIndex === -1) return;

      const currentContent = currentParagraph.innerHTML;
      const cursorPosition = range.startOffset;

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

      // Create new paragraph with same list properties
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
      

      // Set cursor position to new paragraph
      setTimeout(() => {
        const newElement = document.getElementById(newParagraph.id);
        if (newElement) {
          const range = document.createRange();
          range.setStart(newElement, 0);
          range.collapse(true);

          const selection = window.getSelection();
          if (selection) {
            selection.removeAllRanges();
            selection.addRange(range);
          }
        }
      }, 0);
    }
  }

  toggleParagraphType(type: 'bullet' | 'number'): void {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);

    // Get start and end paragraphs
    let startNode = range.startContainer;
    let endNode = range.endContainer;

    // Find the containing paragraphs using proper type checking and casting
    let startParagraph =
      startNode.nodeType === Node.TEXT_NODE
        ? (startNode.parentElement as HTMLElement)?.closest('p')
        : (startNode as HTMLElement).closest('p');
    let endParagraph =
      endNode.nodeType === Node.TEXT_NODE
        ? (endNode.parentElement as HTMLElement)?.closest('p')
        : (endNode as HTMLElement).closest('p');

    if (!startParagraph || !endParagraph) {
      // Fallback to traversing up if closest doesn't find paragraphs
      let current = startNode;
      while (current && current.nodeName !== 'P' && current.parentNode) {
        current = current.parentNode;
      }
      startParagraph = current as HTMLParagraphElement;

      current = endNode;
      while (current && current.nodeName !== 'P' && current.parentNode) {
        current = current.parentNode;
      }
      endParagraph = current as HTMLParagraphElement;

      if (!startParagraph || !endParagraph) return;
    }

    // Get all affected paragraphs
    const affectedParagraphs = this.getElementsBetween(
      startParagraph,
      endParagraph
    );

    // Check if all selected paragraphs already have the target type
    const allHaveTargetType = affectedParagraphs.every((p) => {
      const paragraph = this.paragraphs.find((para) => para.id === p.id);
      return paragraph?.type === type;
    });

    // Toggle type for all affected paragraphs
    affectedParagraphs.forEach((p, index) => {
      const paragraphIndex = this.paragraphs.findIndex(
        (para) => para.id === p.id
      );
      if (paragraphIndex !== -1) {
        // If all paragraphs already have the target type, remove it
        // Otherwise, apply the target type
        this.paragraphs[paragraphIndex].type = allHaveTargetType
          ? 'none'
          : type;

        // Maintain current level if it exists, otherwise set to 0
        if (this.paragraphs[paragraphIndex].type === 'none') {
          this.paragraphs[paragraphIndex].level = 0;
        }
      }
    });

    // Maintain selection
    const newRange = document.createRange();
    newRange.setStart(range.startContainer, range.startOffset);
    newRange.setEnd(range.endContainer, range.endOffset);

    this.renderParagraphs();

    // Restore selection
    selection.removeAllRanges();
    selection.addRange(newRange);
  }


  onEditorClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (target.tagName === 'P') {
      this.selectParagraph(target.id);
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
      .querySelectorAll('p')
      .forEach((p: HTMLElement) => {
        p.classList.remove('selected');
      });

    const selectedElement = document.getElementById(id);
    if (selectedElement) {
      selectedElement.classList.add('selected');
    }
    if (this.selectedParagraphIds.length > 0) {
      this.paragraphs.forEach((p) => {
        const pEl = document.getElementById(p.id);
        if (this.selectedParagraphIds?.includes(p.id)) {
         
          if (pEl) {
            pEl.classList.add('grouped');
          }
        } else {
          if (pEl) {
            pEl.classList.remove('grouped');
          }
        }

      });
    }
  }


  applyStyle(property: string, value: string): void {
    if (!this.selectedParagraphId) return;

    const paragraph = this.paragraphs.find(
      (p) => p.id === this.selectedParagraphId
    );
    if (paragraph) {
      paragraph.styles = {
        ...paragraph.styles,
        [property]: value,
      };
      this.renderParagraphs();

      const p = document.getElementById(this.selectedParagraphId);
      if (p) {
        p.classList.add('selected');
      }
    }
  }

  deleteParagraph(): void {
    if (!this.selectedParagraphId) return;

    const index = this.paragraphs.findIndex(
      (p) => p.id === this.selectedParagraphId
    );
    if (index !== -1) {
      this.paragraphs.splice(index, 1);

      if (this.paragraphs.length === 0) {
        this.createNewParagraph();
      }

      this.selectedParagraphId = null;
      this.renderParagraphs();
    }
  }

  getParagraphs(): Paragraph[] {
    return this.paragraphs;
  }



  addNote(paragraphId: string, content: string): void {
    const paragraph = this.paragraphs.find(p => p.id === paragraphId);
    if (!paragraph) return;
  
    const newNote: ParagraphNote = {
      id: crypto.randomUUID(),
      content,
      createdAt: new Date(),
      updatedAt: new Date()
    };
  
    paragraph.notes.push(newNote);
    // You might want to trigger change detection or re-render here
  }
  
  updateNote(paragraphId: string, noteId: string, content: string): void {
    const paragraph = this.paragraphs.find(p => p.id === paragraphId);
    if (!paragraph) return;
  
    const note = paragraph.notes.find(n => n.id === noteId);
    if (!note) return;
  
    note.content = content;
    note.updatedAt = new Date();
  }
  
  deleteNote(paragraphId: string, noteId: string): void {
    const paragraph = this.paragraphs.find(p => p.id === paragraphId);
    if (!paragraph) return;
  
    paragraph.notes = paragraph.notes.filter(n => n.id !== noteId);
  }
  
  getNotes(paragraphId: string): ParagraphNote[] {
    const paragraph = this.paragraphs.find(p => p.id === paragraphId);
    return paragraph?.notes || [];
  }

  showNoteEditor = false;
  editingNote: ParagraphNote | null = null;

  onNoteSave(content: string) {
    if (this.editingNote) {
      this.updateNote(this.selectedParagraphId!, this.editingNote.id, content);
    } else {
      this.addNote(this.selectedParagraphId!, content);
    }
    this.showNoteEditor = false;
    this.editingNote = null;
  }

  onNoteCancel() {
    this.showNoteEditor = false;
    this.editingNote = null;
  }

  onNoteEdit(note: ParagraphNote) {
    this.editingNote = note;
    this.showNoteEditor = true;
  }

  onNoteDelete(note: ParagraphNote) {
    if (this.selectedParagraphId) {
      this.deleteNote(this.selectedParagraphId, note.id);
    }
  }

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
}

// Breakpoint

// interface Paragraph {
//   id: string;
//   content: string;
//   styles: {
//     fontSize?: string;
//     fontWeight?: string;
//     color?: string;
//     textAlign?: string;
//     minHeight?: string;
//   };
//   type: 'bullet' | 'number' | 'none';
//   level: number; // Indentation level
// }
