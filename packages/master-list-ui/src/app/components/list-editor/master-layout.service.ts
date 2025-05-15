import { BehaviorSubject, Subject } from 'rxjs';
import { NoteItemTag, Paragraph } from '../../types/note';
import { ElementRef, Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { TagCssGenerator } from '../../services/tag-css-generator';
import { TagApiService } from '../../services/tag-api';
import { NotesApiService } from '../../services/notes-api.service';

@Injectable({
  providedIn: 'root',
})
export class MasterLayoutService {
  selectedParagraphId: string | null = null;
  selectedParagraphIds: string[] = [];
  affectedRows: Paragraph[] = [];
  editorRef!: ElementRef;
  loadOriginParagraph = new BehaviorSubject<Paragraph | null>(null);
  clipBoard: Paragraph[] = [];

  selectedHighlightTag: string | null = null

  public ctrlDown = false;
  public shiftDown = false;
  constructor(
    private notesApi: NotesApiService,
    private tagApi: TagApiService,
    private tagColorService: TagCssGenerator,
    private toastr: ToastrService
  ) {}
  public setEditorRef(editorRef: any) {
    this.editorRef = editorRef;
  }
  public setChangeSubject(changeSubject: Subject<void>) {
    this.changeSubject = changeSubject;
  }

  private changeSubject!: Subject<void>;

  unassignTag(tags: string[], paragraphs: Paragraph[]) {
    this.applyInlineStyle('', paragraphs); // updates the affected rows
    const map = new Map<string, Paragraph>(paragraphs.map((x) => [x.id, x]));
    if (this.affectedRows.length > 0) {
      this.affectedRows.forEach((r) => {
        r.tags = r.tags.filter((x) => !tags.find(a => x.name == a));
        const p = map.get(r.id);
        if (p) {
          p.tags = p.tags.filter((x) => !tags.find(a => x.name == a));
        }
      });
    } else if (this.selectedParagraphIds) {
      this.selectedParagraphIds.forEach((x) => {
        const item = map.get(x);
        if (item) {
          item.tags = item.tags.filter((x) => !tags.find(a => x.name == a));
        }
      });
    }
    this.renderParagraphs(paragraphs);
  }
  assignTagToRows(tagName: string, paragraphs: Paragraph[]) {
    this.setAffectedRange(paragraphs);
    const map = new Map<string, Paragraph>(paragraphs.map((x) => [x.id, x]));
    if (this.affectedRows.length > 0) {
      this.affectedRows.forEach((r) => {
        const foundTag = r.tags.find((x) => x.name === tagName);
        if (!foundTag) {
          const newTag: NoteItemTag = { id: null, name: tagName, sort_order: null };
          r.tags.push(newTag)
        const p = map.get(r.id);
        if (p) {
          p.tags = this.duplicateTags(r.tags, true);
        }
      }
      });
    } else if (this.selectedParagraphIds) {
      this.selectedParagraphIds.forEach((x) => {
        const item = map.get(x);
        if (item) {
          const foundTag = item.tags.find((x) => x.name === tagName);
          if (!foundTag) {
            const newTag: NoteItemTag = { id: null, name: tagName, sort_order: null };
            item.tags.push(newTag);
          }
        }
      });
    }
    this.renderParagraphs(paragraphs);
  }
  public cutNoteItems(paragraphs: Paragraph[]) : Paragraph[] {
    this.clipBoard = [];
    this.setAffectedRange(paragraphs);
    const map = new Map<string, Paragraph>(paragraphs.map((x) => [x.id, x]));

    if (this.affectedRows.length > 0) {
      this.clipBoard = this.affectedRows;
      paragraphs = paragraphs.filter((x) => {
        return !this.affectedRows.find((r) => r.id === x.id);
      });

    } else if (this.selectedParagraphIds) {
      this.selectedParagraphIds.forEach((x) => {
        const item = map.get(x);
        if (item) {
          this.clipBoard.push(item);
        }
      });
      paragraphs = paragraphs.filter((x) => {
        return !this.selectedParagraphIds?.find((r) => r === x.id);
      });
    }
    this.renderParagraphs(paragraphs);
    return paragraphs;
  }

  public pasteNoteItems(paragraphs: Paragraph[]): Paragraph[] {
    if (this.clipBoard.length === 0) {
      return paragraphs;
    }
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return paragraphs;

    const range = selection.getRangeAt(0);

    // Get start and end nodes
    let startNode = range.startContainer;
   
    // Find the containing content divs and editor rows
    let startContentDiv = this.findParentWithClass(startNode, 'content-div');
    if (!startContentDiv) return paragraphs;
    let startEditorRow = this.findParentWithClass(
      startContentDiv,
      'editor-row'
    );
    // let editorRow = startContentDiv.closest('.editor-row');
    if (!startEditorRow /*|| !editorRow */) return paragraphs;
    
    const id  = startEditorRow.id;
    const selectedParagraph = paragraphs.find(
      (x) => x.id === id
    );

    




      
      if (selectedParagraph) {
        const index = paragraphs.indexOf(selectedParagraph);
        paragraphs.splice(index + 1, 0, ...this.clipBoard);
      }

    this.renderParagraphs(paragraphs);
    this.clipBoard = [];
    return paragraphs;
  }

  setAffectedRange(paragraphs: Paragraph[]) {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;
    const range = selection.getRangeAt(0);
    let startNode = range.startContainer;
    let endNode = range.endContainer;
    let startContentDiv = this.findParentWithClass(startNode, 'content-div');
    let endContentDiv = this.findParentWithClass(endNode, 'content-div');
    if (!startContentDiv || !endContentDiv) return;

    let startEditorRow = this.findParentWithClass(
      startContentDiv,
      'editor-row'
    );
    let endEditorRow = this.findParentWithClass(endContentDiv, 'editor-row');
    if (!startEditorRow || !endEditorRow) return;
    // Handle single editor row case
    if (startEditorRow === endEditorRow) {
      
      this.setAffectedElements([], paragraphs);
    }
    // Handle multiple editor rows
    else {
      // Get all affected editor rows
      const affectedRows = this.getElementsBetween(
        startEditorRow,
        endEditorRow
      );

      this.setAffectedElements(affectedRows, paragraphs);
    }
  }



  applyInlineStyle(style: string, paragraphs: Paragraph[]): void {
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
    let startEditorRow = this.findParentWithClass(
      startContentDiv,
      'editor-row'
    );
    let endEditorRow = this.findParentWithClass(endContentDiv, 'editor-row');

    if (!startEditorRow || !endEditorRow) return;
    // Create the style span
    // below is not unselecting because new spans are being created, need to reverse the
    // creation of the spans
    const span = document.createElement('span');
    switch (style) {
      case 'bold':
        // This doesn't work need to find another way
        if (span.style.fontWeight == 'bold') {
          span.style.fontWeight = 'normal';
        } else {
          span.style.fontWeight = 'bold';
        }
        break;
      case 'italic':
        span.style.fontStyle = 'italic';
        break;
      case 'large':
        span.style.fontSize = '1.2em';
        break;
      case 'strike':
        // This doesn't work need to find another way
        console.log('text dec', span.style);
        if (span.style.textDecoration === 'line-through') {
          span.style.textDecoration = 'initial';
        } else {
          span.style.textDecoration = 'line-through';
        }
    }

    // Handle single editor row case
    if (startEditorRow === endEditorRow) {
      const content = range.extractContents();
      span.appendChild(content);
      range.insertNode(span);
      this.setAffectedElements([], paragraphs);
    }
    // Handle multiple editor rows
    else {
      // Get all affected editor rows
      const affectedRows = this.getElementsBetween(
        startEditorRow,
        endEditorRow
      );

      if (style === 'merge') {
        // The edited paragraph is going up to the top and the first line of taht paragraph still has a paragraph at
        // with that id (selecing colors the top) the previous positoin
        // then pressing enter deltes the compound paragraph
        // console.log('one', paragraphs.map(x => x.id))
        this.mergeParagraphs(affectedRows, paragraphs);
        selection.removeAllRanges();
        this.renderParagraphs(paragraphs);
        return;
      }
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
      this.setAffectedElements(affectedRows, paragraphs);
    }

    // Update our data model
    this.updateParagraphContent(paragraphs);

    // Restore selection
    selection.removeAllRanges();
    selection.addRange(range);
  }

  // Creating a duplicatge paragraph and putting it at the top
  private mergeParagraphs(affectedRows: any[], paragraphs: Paragraph[]) {
   
    const firstItem = affectedRows[0];
    let contentX = paragraphs.find(x => x.id === firstItem.id);
    const two = paragraphs.filter(x => x.id === contentX!.id)

    const firstContent =  firstItem.querySelector('.content-div');;
    const idMap = new Map<string, Paragraph>(paragraphs.map(x => ([x.id, x])));

    affectedRows.slice(1, affectedRows.length).forEach((r, i) => {
      const br = document.createElement('br');
     
      const rowContent = r.querySelector('.content-div');
      // const firstContent = firstItem.querySelector('.content-div');;
      firstContent.appendChild(br);
      firstContent.innerHTML = firstContent.innerHTML + rowContent.innerHTML;
      
      const id = idMap.get(r.id)!
      const paraIndex = paragraphs.indexOf(id)
      paragraphs.splice(paraIndex, 1);
      
    })
    const contentDiv = firstItem.querySelector('.content-div');
    contentX!.content = contentDiv.innerHTML as string;

    // 2 paragraphs being created
    const changedpara = paragraphs.filter(x => x.id === contentX!.id)
  }

  // When a tag or tags are assigned, use applyInlineStyle function that uses this function
  // to aggregate selected paragraphs. Either use affectedRows or then selectedParagraphs (background yellow)
  // to associate tag then add class name to bullet points for color and dynamically set color with css variables
  private setAffectedElements(affectedRows: any[], paragraphs: Paragraph[]) {
    const ids = new Map<string, boolean>(affectedRows.map((x) => [x.id, true]));
    this.affectedRows = paragraphs.filter((x) => {
      return ids.get(x.id);
    });
  }

  // Helper method to find parent element with a specific class
  private findParentWithClass(
    node: Node,
    className: string
  ): HTMLElement | null {
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
      if (!currentElement || !currentElement.classList.contains('editor-row'))
        break;
    }

    return elements;
  }

  private duplicateTags(tags: NoteItemTag[], copyTagSort: boolean): NoteItemTag[] {
    if (!copyTagSort) {
      return tags.map((tag) => ({ ...tag, sort_order: null }));
    }
    return tags.map((tag) => ({ ...tag }));
  }
  // Update the updateParagraphContent method to work with the new structure
  // Aaron: Commenting out this for now, do I need it?
  private updateParagraphContent(paragraphs: Paragraph[]): void {
    const rowElements =
      this.editorRef.nativeElement.querySelectorAll('.editor-row');

    const newParagraphs = Array.from(rowElements).map((row: any) => {
      const contentDiv = row.querySelector('.content-div');
      const existingParagraph = paragraphs.find((para) => para.id === row.id);

      return {
        id: row.id,
        content: contentDiv.innerHTML,
        styles: existingParagraph?.styles || {
          fontSize: '16px',
          textAlign: 'left',
        },
        type: existingParagraph?.type || 'none',
        level: existingParagraph?.level || 0,
        notes: existingParagraph?.notes || [],
        tags: this.duplicateTags(existingParagraph?.tags || [], true),
        updatedAt: existingParagraph?.updatedAt || new Date(),
        createdAt: existingParagraph?.createdAt || new Date(),
        creation_list_id: existingParagraph?.creation_list_id || null,
        creation_type: existingParagraph?.creation_type || null,
        origin_sort_order: existingParagraph?.origin_sort_order, // Need to implement this as null not undefined
      };
    });
    paragraphs.length = 0;
    paragraphs.push(...newParagraphs);
  }

  ngAfterViewInit(editorRef: any, paragraphs: Paragraph[]): Paragraph[] {
    this.editorRef = editorRef;
    if (!paragraphs.length) {
      this.createNewParagraph(paragraphs);
    }
    this.renderParagraphs(paragraphs);

    // Set focus to the first paragraph
    const firstP = editorRef.nativeElement.querySelector('p');
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
    return paragraphs;
  }

  onDocumentChange(): void {
    // Ensure positions are always up-to-date in memory
    // This is used when clearing errors
    // this.isDirty = true;
    this.changeSubject.next();
  }
  private createNewParagraph(
    paragraphs: Paragraph[],
    content: string = '',
    level: number = 0
  ): void {
    const timestamp = Date.now();
    const randomUuid = crypto.randomUUID();
    const id = randomUuid; //`${timestamp}-${randomUuid}`;

    const paragraph: Paragraph = {
      id,
      content: content,
      styles: {
        fontSize: '16px',
        textAlign: 'left',
        minHeight: '24px',
      },
      type: 'none',
      level: level,
      notes: [],
      tags: [],
      updatedAt: new Date(),
      createdAt: new Date(),
      creation_list_id: null,
      creation_type: null,
    };

    paragraphs.push(paragraph);
    this.renderParagraphs(paragraphs);
  }

  public setHighlightName(paragraphs: Paragraph[], name: string) {
    this.selectedHighlightTag = name;
    this.renderParagraphs(paragraphs);
  }

  private renderParagraphs(paragraphs: Paragraph[]): void {
    this.onDocumentChange();

    let allTags = paragraphs.reduce((tags: NoteItemTag[], paragraph) => {
      if (paragraph.tags && Array.isArray(paragraph.tags)) {
        return [...tags, ...paragraph.tags];
      }
      return tags;
    }, []);

    // undefined is showing up in tags
    allTags = allTags.filter(x => x);
    const names = allTags.map(x => x.name);

    // Call the service to ensure we have styles for all tags
    this.tagColorService.ensureTagStyles(names);

    const editor = this.editorRef.nativeElement;
    editor.innerHTML = '';

    paragraphs.forEach((paragraph, i: number) => {
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

      // Apply tag-based classes to bullets
      this.applyTagClassesToBullets(paragraph.tags || [], [
        contentDiv,
        level1,
        level2,
        level3,
      ]); ////[level3, level2, level1, contentDiv]);

        this.applyTagClassToContent(
            paragraph.tags || [],
            this.selectedHighlightTag,
            contentDiv
        );
      
        

      // Add the nested structure to the editor
      outerDiv.appendChild(level3);
      editor.appendChild(outerDiv);

      // Mark this row with its type if it's a list item
      if (paragraph.type === 'number' || paragraph.type === 'bullet') {
        outerDiv.setAttribute('data-list-type', paragraph.type);
      }
    });
  }

  /**
   * Applies CSS classes to bullet elements based on the paragraph's tags
   * @param tags Array of tag strings from the paragraph
   * @param bulletElements Array of the 4 nested bullet div elements
   */
  private applyTagClassesToBullets(
    tags: NoteItemTag[],
    bulletElements: HTMLElement[]
  ): void {
    // We'll handle up to 4 tags, one for each bullet level
    const maxBullets = 4;

    // Take only the first 4 tags (if there are more)
    const tagsToUse = tags.slice(0, maxBullets);

    // Apply CSS classes to the corresponding bullet elements
    bulletElements.forEach((element, index) => {
      // First, remove any existing tag classes to avoid conflicts
      element.classList.forEach((className) => {
        if (className.startsWith('tag-')) {
          element.classList.remove(className);
        }
      });

      // If we have a tag for this bullet level, apply a class based on the tag
      if (index < tagsToUse.length) {
        const tag = tagsToUse[index];
        // Use the service to generate the sanitized class name
        const tagClass = `tag-${this.tagColorService.sanitizeTagForCssClass(
          tag.name
        )}`;
        element.classList.add(tagClass);
      } else {
        // If we don't have a tag for this bullet level, apply a default white color class
        element.classList.add('tag-default');
      }
    });
  }

  applyTagClassToContent(
    tags: NoteItemTag[],
    selectedHighlightTag: string | null,
    contentDiv: HTMLElement
  ) {
    contentDiv.classList.forEach((className) => {
      if (className.startsWith('highlight-')) {
        contentDiv.classList.remove(className);
      }
    });
    if(selectedHighlightTag === null) {
        return;
    }
    if (selectedHighlightTag === '' && tags.length > 0) {
        const tag = tags[0];
        const tagClass = `highlight-${this.tagColorService.sanitizeTagForCssClass(
            tag.name
          )}`;
        contentDiv.classList.add(tagClass);
    } else if (selectedHighlightTag)  {
        
      const foundTag = tags.find(x => x.name === selectedHighlightTag);
      if (foundTag) {
        const tag = foundTag;
        const tagClass = `highlight-${this.tagColorService.sanitizeTagForCssClass(
            tag.name
          )}`;
        contentDiv.classList.add(tagClass);
      }
    }
  }

  onInput(event: Event, paragraphs: Paragraph[]): void {
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
        // paragraphs.unshift({
        //   id: outerDiv.id,
        //   content: contentDiv.innerHTML,
        //   styles: {
        //     fontSize: '16px',
        //     textAlign: 'left',
        //     minHeight: '24px',
        //   },
        //   type: 'none',
        //   level: 0,
        //   notes: [],
        //   tags: [],
        //   updatedAt: new Date(),
        //   createdAt: new Date()
        // });
      }
    });

    this.updateParagraphContent(paragraphs);
  }

  onKeyDown(paragraphs: Paragraph[], event: KeyboardEvent): void {
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
        if (
          node.nodeType === Node.ELEMENT_NODE &&
          (node as HTMLElement).classList.contains('editor-row')
        ) {
          editorRow = node;
          break;
        }
        node = node.parentNode!;
      }

      if (!editorRow) return;
      const currentParagraph = editorRow as HTMLElement;

      const currentIndex = paragraphs.findIndex(
        (p) => p.id === currentParagraph.id
      );
      if (currentIndex === -1) return;

      // Get content from the content div
      const contentDiv = currentParagraph.querySelector('.content-div');
      const currentContent = contentDiv ? contentDiv.innerHTML : '';

      // Check if we're at the end of an empty paragraph
      const isEmptyParagraph =
        currentContent.trim() === '' || currentContent === '<br>';

      // If Ctrl/Meta key is pressed, insert a line break instead of creating a new paragraph
      if (this.ctrlDown || this.shiftDown) {
        // Insert a line break at the current cursor position
        const br = document.createElement('br');
        range.deleteContents();
        range.insertNode(br);

        // Move the cursor after the inserted line break
        range.setStartAfter(br);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);

        // Update the paragraph content in your data model
        if (contentDiv) {
          paragraphs[currentIndex].content = contentDiv.innerHTML;
        }
        this.onDocumentChange();
        return;
      }

      // Handle enter press with cursor inbetween text
      const afterCursorRange = range.cloneRange();
      afterCursorRange.selectNodeContents(contentDiv!);
      afterCursorRange.setStart(range.endContainer, range.endOffset);

      const afterCursorFragment = afterCursorRange.extractContents();
      const div = document.createElement('div');
      div.appendChild(afterCursorFragment);
      const afterCursorHTML = div.innerHTML || '<br>';

      // Update current paragraph's content
      paragraphs[currentIndex].content = contentDiv!.innerHTML || '<br>';

      // Create new paragraph with extracted content
      const newParagraph: Paragraph = {
        id: crypto.randomUUID(),
        content: afterCursorHTML,
        styles: { ...paragraphs[currentIndex].styles },
        type: paragraphs[currentIndex].type,
        level: paragraphs[currentIndex].level,
        notes: paragraphs[currentIndex].notes,
        tags:  this.duplicateTags(paragraphs[currentIndex].tags || [], false),
        updatedAt: new Date(),
        createdAt: new Date(),
        creation_list_id: null,
        creation_type: null,
      };

      // Insert new paragraph
      paragraphs.splice(currentIndex + 1, 0, newParagraph);
      this.renderParagraphs(paragraphs);

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

  onTabKey(paragraphs: Paragraph[], event: KeyboardEvent): void {
    // Prevent default tab behavior (which would move focus to next element)
    event.preventDefault();

    // Handle the tab insertion
    this.insertTabAtCursor(paragraphs, event.shiftKey);
  }
  private insertTabAtCursor(
    paragraphs: Paragraph[],
    isShiftTab: boolean = false
  ): void {
    const selection = window.getSelection();
    if (!selection) return;

    const range = selection.getRangeAt(0);
    let currentNode = range.commonAncestorContainer;

    // Find the containing editor row
    let editorRow = null;
    let node = currentNode;
    while (node && !editorRow) {
      if (
        node.nodeType === Node.ELEMENT_NODE &&
        (node as HTMLElement).classList.contains('editor-row')
      ) {
        editorRow = node;
        break;
      }
      node = node.parentNode!;
    }

    if (!editorRow) return;
    const currentParagraph = editorRow as HTMLElement;

    // Find the corresponding paragraph in our data model
    const currentIndex = paragraphs.findIndex(
      (p) => p.id === currentParagraph.id
    );
    if (currentIndex === -1) return;

    // Get content div
    const contentDiv = currentParagraph.querySelector('.content-div');
    if (!contentDiv) return;

    this.insertTabCharacter(range, selection);

    // Update paragraph content in data model
    paragraphs[currentIndex].content = contentDiv.innerHTML;
    this.onDocumentChange();
  }
  /**
   * Inserts a tab character (4 spaces) at the cursor position
   */
  private insertTabCharacter(range: Range, selection: Selection): void {
    // Create a text node with 4 non-breaking spaces (equivalent to a tab)
    const tabSpaces = document.createTextNode('\u00A0\u00A0\u00A0\u00A0');

    // Insert at cursor position
    range.deleteContents();
    range.insertNode(tabSpaces);

    // Move cursor after the inserted tab
    range.setStartAfter(tabSpaces);
    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  onEditorClick(paragraphs: Paragraph[], event: MouseEvent): void {
    const target = event.target as HTMLElement;
    let editorRow = target.closest('.editor-row');

    if (editorRow) {
      this.selectParagraph(paragraphs, editorRow.id);
    }
  }

  setLoadOriginLink(paragraphs: Paragraph[], id: string){
    const p = paragraphs.find( x => x.id === id);
    if (p) {
      this.loadOriginParagraph.next(p);
    }
  }

  selectParagraph(paragraphs: Paragraph[], id: string): void {
    this.selectedParagraphId = id;
    this.setLoadOriginLink(paragraphs, id);
    if (this.ctrlDown) {
      if (this.selectedParagraphIds?.includes(id)) {
        this.selectedParagraphIds = this.selectedParagraphIds?.filter(
          (pId) => pId !== id
        );
      } else {
        this.selectedParagraphIds?.push(id);
      }
    } else {
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
      paragraphs.forEach((p) => {
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

  handlePaste(event: ClipboardEvent, paragraphs: Paragraph[]) {
    // Prevent default paste behavior
    event.preventDefault();

    // Get the pasted text content
    const pastedText = event.clipboardData?.getData('text') || '';

    // Check if the content appears to be code
    const isLikelyCode = false; //this.isCodeContent(pastedText);

    let currentIndex = paragraphs.length - 1;
    if (this.selectedParagraphId) {
      currentIndex = paragraphs.findIndex(
        (p) => p.id === this.selectedParagraphId
      );
    }

    if (isLikelyCode) {
      // Handle as code - create a single div with all content
      const newParagraph: Paragraph = {
        id: crypto.randomUUID(),
        content: pastedText, // Keep all content together
        styles: {
          ...paragraphs[currentIndex].styles,
          fontFamily: 'monospace', // Apply code styling
          whiteSpace: 'pre', // Preserve whitespace
        },
        type: 'code', // Mark this as code type
        level: paragraphs[currentIndex].level,
        notes: paragraphs[currentIndex].notes,
        tags: this.duplicateTags(paragraphs[currentIndex].tags || [], false),
        updatedAt: paragraphs[currentIndex].updatedAt,
        createdAt: paragraphs[currentIndex].createdAt,
        creation_list_id: null,
        creation_type: null,
      };

      // Insert the code paragraph
      paragraphs.splice(currentIndex + 1, 0, newParagraph);
    } else {
      // Handle as regular text - split by newlines as before
      const lines = pastedText
        .split(/\r?\n/)
        .filter((line) => line.trim().length > 0); // Remove empty lines

      // Create new paragraphs for each line
      lines.forEach((line, i) => {
        const newParagraph: Paragraph = {
          id: crypto.randomUUID(),
          content: line,
          styles: { ...paragraphs[currentIndex].styles },
          type: paragraphs[currentIndex].type,
          level: paragraphs[currentIndex].level,
          notes: paragraphs[currentIndex].notes,
          tags: this.duplicateTags(paragraphs[currentIndex].tags || [], false),
          updatedAt: new Date(),
          createdAt: new Date(),
          creation_list_id: null,
          creation_type: null,
        };

        // Insert new paragraph
        paragraphs.splice(currentIndex + 1 + i, 0, newParagraph);
      });
    }

    this.renderParagraphs(paragraphs);

    // Clear the paste area
    if (event.target instanceof HTMLElement) {
      event.target.textContent = '';
    }
  }

  // Helper method to detect if content is likely code
  private isCodeContent(text: string): boolean {
    // Various heuristics to detect code:

    // 1. Check for common code patterns
    const codePatterns = [
      /[{}\[\]();][\s\S]*[{}\[\]();]/, // Contains brackets, parentheses, etc.
      /\b(function|const|let|var|if|for|while|class|import|export)\b/, // Common keywords
      /^\s*[a-zA-Z0-9_$]+\s*\([^)]*\)\s*{/m, // Function definition pattern
      /^\s*import\s+.*\s+from\s+['"][^'"]+['"];?\s*$/m, // Import statement
      /^\s*<[a-zA-Z][^>]*>[\s\S]*<\/[a-zA-Z][^>]*>\s*$/m, // HTML-like tags
      /\$\{.*\}/, // Template literals
      /\b(public|private|protected)\b.*\(/, // Method definitions
    ];

    // 2. Check for consistent indentation (code usually has structured indentation)
    const lines = text.split(/\r?\n/);
    const indentationPattern = lines
      .filter((line) => line.trim().length > 0)
      .map((line) => line.match(/^\s*/)?.[0].length || 0);

    const hasConsistentIndentation =
      indentationPattern.length > 3 &&
      new Set(indentationPattern).size > 1 &&
      new Set(indentationPattern).size < indentationPattern.length / 2;

    // 3. Check for code-to-text ratio (code usually has more special characters)
    const specialCharsCount = (
      text.match(/[{}[\]();:.,<>?!&|^%*+=/\\-]/g) || []
    ).length;
    const textLength = text.length;
    const specialCharRatio = specialCharsCount / textLength;

    // 4. Check for multi-line with specific structure
    const hasMultipleLines = lines.length > 2;

    // Return true if any of the code patterns are found or multiple indicators are present
    return (
      codePatterns.some((pattern) => pattern.test(text)) ||
      (hasMultipleLines && (hasConsistentIndentation || specialCharRatio > 0.1))
    );
  }
}
