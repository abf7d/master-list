import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  computed,
  DestroyRef,
  effect,
  ElementRef,
  HostListener,
  inject,
  Injector,
  input,
  linkedSignal,
  output,
  signal,
  ViewChild,
  ViewEncapsulation,
} from '@angular/core';
import { ParagraphNote, Paragraph } from '../../types/note';
import { MetaTagService } from '../meta-tags/meta-tag.service';
import { MetaTagsComponent } from '../meta-tags/meta-tags.component';
import { NotesApiService } from '../../services/notes-api.service';
import { TagCssGenerator } from '../../services/tag-css-generator';
import { BehaviorSubject, debounceTime, interval, Observable, skip, Subject, tap } from 'rxjs';
import { TagSelection, TagSelectionGroup } from '../../types/tag';
import { TagApiService } from '../../services/tag-api';
import { ToastrService } from 'ngx-toastr';
import { MasterLayoutService } from './master-layout.service';
import { NavListComponent } from '../nav-list/nav-list.component';
import { MsalService } from '@azure/msal-angular';
import { AuthCoreService } from '@master-list/auth';
// import { MsalService } from '@master-list/auth';
// import { NoteEditorComponent } from '../note-editor/note-editor.component';
// import { NotesPanelComponent } from '../notes-panel/notes-panel.component';

@Component({
  selector: 'app-master-layout',
  imports: [
    CommonModule,
    MetaTagsComponent,
    NavListComponent
    // NoteEditorComponent,
    // NotesPanelComponent
  ],
  templateUrl: './master-layout.component.html',
  styleUrl: './master-layout.component.scss',
  encapsulation: ViewEncapsulation.None,
})

// BREAKPOINT 2!!!!
export class MasterLayoutComponent implements AfterViewInit {
  // readonly firstSignal = signal(42);
  // readonly secondSignal = signal(10);
  // readonly derived = computed(
  //   () => this.firstSignal() * 2 + this.secondSignal()
  // );
  // readonly products = signal(['Apple', 'Banana', 'Cherry']);
  // // linkedSignal is both writable and computed at the same time
  // // when one of the dependent signals change like products, it
  // // re-evaluates the value. So you can update the value and recalculate when
  // // an iternal signal changes
  // readonly selectedProduct = linkedSignal(() => this.products()[0]);
  // // This linkedSignal is an alternative to useing an effect
  // readonly moreComplexSelectedProduct = linkedSignal<string[], string>({
  //   //<typeOfSource, typeOfReturn>
  //   source: this.products,
  //   computation: (prod, prev) => {
  //     //prod[0] // prod is the new value for products (source), but the computation doesn't have to depend on products, you can choose here
  //     if (!prev) return prod[0];
  //     if (prod.includes(prev.value)) return prev.value;
  //     return prod[0];
  //   },
  // });
  // readonly destroyRef = inject(DestroyRef); //; inject can only happen here or in a constructor
  // readonly injector = inject(Injector);
  // readonly inputvar1 = input.required<number>(); // a required input with no value for initiailzation
  // readonly inputvar2 = input('usd');
  // readonly assignTag = output<void>();

  //use interfval rxjs to check to queue for saving

  @ViewChild('editor') editorRef!: ElementRef;

  tagGroup$: BehaviorSubject<TagSelectionGroup> = new BehaviorSubject<TagSelectionGroup>({ name: 'Lists', tags: []});
  paragraphs: Paragraph[] = []
  // selectedParagraphId: string | null = null;
  // selectedParagraphIds: string[] = [];
  // selectedTab = 'tags';


  private changeSubject = new Subject<void>();
  // private isDirty = false;
  private isSaving = false;
  public error = false;
  private noteId!: string;
  public popListOut = false;
 
  affectedRows: Paragraph[] = [];
  constructor(
    private notesApi: NotesApiService,
    private tagApi: TagApiService,
    private tagColorService: TagCssGenerator,
    private toastr: ToastrService,
    private manager: MasterLayoutService,
    private authService: AuthCoreService
  ) // private destroyRef: DestroyRef
  {
    this.manager.setChangeSubject(this.changeSubject);
    this.changeSubject.pipe(
      debounceTime(2000), // 2 seconds of inactivity
      skip(1),
    ).subscribe(() => {
      if (/*this.isDirty &&*/ !this.isSaving && !this.error) {
        // this.isDirty = false;
        
        this.isSaving = true;
        this.updateParagraphPositions();
        this.notesApi.saveNote(this.paragraphs, this.noteId).subscribe({
        next: result => {
          if (result.message === 'success') {
            this.isSaving = false;
          }
        },
        error: result => {
          this.error = true;
          this.isSaving = false;
          this.toastr.error('Note not saved', 'Error');
        }
      });
    }
    });

    // HotModuleReload wasn't calling ngOnAfterInit (which adds firs paragraph) so I added below to force it
    // Consider taking this out in the future
    // this.manager.ngAfterViewInit(this.editorRef, this.paragraphs)

    // // can't change signal values inside effects
    // // ;you can call async code
    // // you can cause side effects (I think this is like rxjs tap)
    // // this effect has to be in constructor unless you create your own injection context when you use it like as commented out as a second param below
    // effect(
    //   () => {
    //     console.log('first', this.firstSignal());
    //     console.log('second', this.secondSignal());
    //     console.log('computed', this.derived());
    //     //this would break, but somehow you can force it
    //     //this.firstSignal.set(53);
    //   },
    //   {
    //     injector: this.injector,
    //   }
    // );
    // // changing 2 thigns here updates the effect once, things are batched
    // // the first signal and second sgnal are marked as dirty then the effect is run
    // // and processes all of the dirty varialbes once
    // this.firstSignal.update((value) => value + 1);
    // this.firstSignal.set(this.firstSignal() + 2);

    // // const sub = interval(1000).subscribe(console.log);
    // // destroyRef.onDestroy(() => sub.unsubscribe())
  }

  private componentVersion = 0;

  ngOnInit() {
    this.tagApi.getLists().pipe(tap(x => this.tagColorService.initTagColors(x))).subscribe(x=> this.tagGroup$.next(x));
    this.tagGroup$.subscribe()
  }

  ngAfterViewInit() {
    console.log('not called after HotModuleReload after init!!!')
    // if (!this.paragraphs.length) {
    //   this.manager.createNewParagraph(this.paragraphs, '');
    //   // this.paragraphs.push(const newParagraph: Paragraph = {
    //     //     id: crypto.randomUUID(),
    //     //     content: '<br>', // Start with empty content
    //     //     styles: { ...this.paragraphs[currentIndex].styles },
    //     //     type: this.paragraphs[currentIndex].type, // Maintain the list type
    //     //     level: this.paragraphs[currentIndex].level, // Maintain the indentation level
    //     //     notes: this.paragraphs[currentIndex].notes,
    //     //     tags: this.paragraphs[currentIndex].tags,
    //     //     updatedAt: this.paragraphs[currentIndex].updatedAt,
    //     //     createdAt: this.paragraphs[currentIndex].createdAt
    //     //   };)
    // }
    this.paragraphs = this.manager.ngAfterViewInit(this.editorRef, this.paragraphs)
    // if (!this.paragraphs.length) {
    //   this.createNewParagraph();
    // }
    // this.renderParagraphs();

    // // Set focus to the first paragraph
    // const firstP = this.editorRef.nativeElement.querySelector('p');
    // if (firstP) {
    //   const range = document.createRange();
    //   range.setStart(firstP, 0);
    //   range.collapse(true);
    //   const selection = window.getSelection();
    //   if (selection) {
    //     selection.removeAllRanges();
    //     selection.addRange(range);
    //   }
    // }
  }
  logOut() {
    this.authService.logout();
  }
  clearError() {
    this.error = false;
    this.changeSubject.next();
  }

  public setHighlight(event: Event): void {
    const name = (event.target as any).value;
    this.manager.setHighlightName(this.paragraphs, name); 

  }
  // onDocumentChange(): void {
  //   // Ensure positions are always up-to-date in memory
  //   // This is used when clearing errors
  //   // this.isDirty = true; 
  //   this.changeSubject.next();
  // }
  
  private updateParagraphPositions(): void {
    // Simple position update - just assign sequential numbers
    this.paragraphs.forEach((paragraph, index) => {
      paragraph.position = index;
    });
  }

  public addTag(tag: TagSelection) {
    this.tagColorService.addTag(tag);
  }
  // nextProduct() {
  //   this.selectedProduct.update((selected) => {
  //     const index = this.products().indexOf(selected);
  //     return this.products()[(index + 1) % this.products().length];
  //   });
  // }

  public assignTagToRows(tagName: string) {
    this.manager.assignTagToRows(tagName, this.paragraphs)
    // this.applyInlineStyle('');
    // const map = new Map<string, Paragraph>(
    //   this.paragraphs.map((x) => [x.id, x])
    // );
    // if (this.affectedRows.length > 0) {
    //   this.affectedRows.forEach((r) => {
    //     r.tags = Array.from(new Set([tagName, ...r.tags]));
    //     const p = map.get(r.id);
    //     if (p) {
    //       p.tags = Array.from(new Set([tagName, ...r.tags]));
    //     }
    //   });
    // } else if (this.selectedParagraphIds) {
    //   this.selectedParagraphIds.forEach((x) => {
    //     const item = map.get(x);
    //     if (item) {
    //       item.tags = Array.from(new Set([tagName, ...item.tags]));
    //     }
    //   });
    // }
    // this.renderParagraphs();
  }

  // Bold, italics, lineThrough click event
  public applyInlineStyle(style: string): void {
    this.manager.applyInlineStyle(style, this.paragraphs)
  }
  //   const selection = window.getSelection();
  //   if (!selection || selection.rangeCount === 0) return;

  //   const range = selection.getRangeAt(0);

  //   // Get start and end nodes
  //   let startNode = range.startContainer;
  //   let endNode = range.endContainer;

  //   // Find the containing content divs and editor rows
  //   let startContentDiv = this.findParentWithClass(startNode, 'content-div');
  //   let endContentDiv = this.findParentWithClass(endNode, 'content-div');

  //   if (!startContentDiv || !endContentDiv) return;

  //   // Find the editor rows that contain these content divs
  //   let startEditorRow = this.findParentWithClass(
  //     startContentDiv,
  //     'editor-row'
  //   );
  //   let endEditorRow = this.findParentWithClass(endContentDiv, 'editor-row');

  //   if (!startEditorRow || !endEditorRow) return;

  //   // Create the style span
  //   // below is not unselecting because new spans are being created, need to reverse the 
  //   // creation of the spans
  //   const span = document.createElement('span');
  //   switch (style) {
  //     case 'bold':
  //       // This doesn't work need to find another way
  //       if (span.style.fontWeight == 'bold') {
  //         span.style.fontWeight = 'normal';
  //       } else {
  //         span.style.fontWeight = 'bold';
  //       }
  //       break;
  //     case 'italic':
  //       span.style.fontStyle = 'italic';
  //       break;
  //     case 'large':
  //       span.style.fontSize = '1.2em';
  //       break;
  //     case 'strike':

  //       // This doesn't work need to find another way
  //       console.log('text dec', span.style)
  //       if (span.style.textDecoration ==='line-through') {
  //       span.style.textDecoration = 'initial';
  //       } else {
  //         span.style.textDecoration = 'line-through';
  //       }
  //   }

  //   // Handle single editor row case
  //   if (startEditorRow === endEditorRow) {
  //     const content = range.extractContents();
  //     span.appendChild(content);
  //     range.insertNode(span);
  //   }
  //   // Handle multiple editor rows
  //   else {
  //     // Get all affected editor rows
  //     const affectedRows = this.getElementsBetween(
  //       startEditorRow,
  //       endEditorRow
  //     );

  //     affectedRows.forEach((row, index) => {
  //       // Find the content div within this row
  //       const contentDiv = row.querySelector('.content-div');
  //       if (!contentDiv) return;

  //       const contentRange = document.createRange();
  //       contentRange.selectNodeContents(contentDiv);

  //       // For first row, start from selection start
  //       if (index === 0) {
  //         contentRange.setStart(range.startContainer, range.startOffset);
  //       }

  //       // For last row, end at selection end
  //       if (index === affectedRows.length - 1) {
  //         contentRange.setEnd(range.endContainer, range.endOffset);
  //       }

  //       // Apply styling to the range
  //       const clonedSpan = span.cloneNode() as HTMLElement;
  //       const content = contentRange.extractContents();
  //       clonedSpan.appendChild(content);
  //       contentRange.insertNode(clonedSpan);
  //     });
  //     this.setAffectedElements(affectedRows);
  //   }

  //   // Update our data model
  //   this.updateParagraphContent();

  //   // Restore selection
  //   selection.removeAllRanges();
  //   selection.addRange(range);
  // }

  // // When a tag or tags are assigned, use applyInlineStyle function that uses this function
  // // to aggregate selected paragraphs. Either use affectedRows or then selectedParagraphs (background yellow)
  // // to associate tag then add class name to bullet points for color and dynamically set color with css variables
  // private setAffectedElements(affectedRows: any[]) {
  //   const ids = new Map<string, boolean>(affectedRows.map((x) => [x.id, true]));
  //   this.affectedRows = this.paragraphs.filter((x) => {
  //     return ids.get(x.id);
  //   });
  //   console.log(this.affectedRows);
  // }

  // // Helper method to find parent element with a specific class
  // private findParentWithClass(
  //   node: Node,
  //   className: string
  // ): HTMLElement | null {
  //   let current = node;

  //   // If it's a text node, start with its parent
  //   if (current.nodeType === Node.TEXT_NODE) {
  //     current = current.parentElement!;
  //   }

  //   // Traverse up the DOM tree looking for an element with the specified class
  //   while (current && current instanceof HTMLElement) {
  //     if (current.classList.contains(className)) {
  //       return current;
  //     }
  //     current = current.parentElement!;
  //   }

  //   return null;
  // }

  // // Helper method to get all editor rows between two elements
  // private getElementsBetween(
  //   startElement: HTMLElement,
  //   endElement: HTMLElement
  // ): HTMLElement[] {
  //   const elements: HTMLElement[] = [];
  //   let currentElement: HTMLElement | null = startElement;

  //   while (currentElement) {
  //     elements.push(currentElement);

  //     if (currentElement === endElement) break;

  //     // Get next editor row
  //     currentElement = currentElement.nextElementSibling as HTMLElement;
  //     if (!currentElement || !currentElement.classList.contains('editor-row'))
  //       break;
  //   }

  //   return elements;
  // }

  // // Update the updateParagraphContent method to work with the new structure
  // private updateParagraphContent(): void {
  //   const rowElements =
  //     this.editorRef.nativeElement.querySelectorAll('.editor-row');

  //   this.paragraphs = Array.from(rowElements).map((row: any) => {
  //     const contentDiv = row.querySelector('.content-div');
  //     const existingParagraph = this.paragraphs.find(
  //       (para) => para.id === row.id
  //     );

  //     return {
  //       id: row.id,
  //       content: contentDiv.innerHTML,
  //       styles: existingParagraph?.styles || {
  //         fontSize: '16px',
  //         textAlign: 'left',
  //       },
  //       type: existingParagraph?.type || 'none',
  //       level: existingParagraph?.level || 0,
  //       notes: existingParagraph?.notes || [],
  //       tags: existingParagraph?.tags || [],
  //       updatedAt: new Date(),
  //       createdAt: existingParagraph?.createdAt || new Date()
  //     };
  //   });
  // }



  // private createNewParagraph(content: string = '', level: number = 0): void {
  //   const timestamp = Date.now();
  //   const randomUuid = crypto.randomUUID();
  //   const id = randomUuid; //`${timestamp}-${randomUuid}`;

  //   const paragraph: Paragraph = {
  //     id,
  //     content: content,
  //     styles: {
  //       fontSize: '16px',
  //       textAlign: 'left',
  //       minHeight: '24px',
  //     },
  //     type: 'none',
  //     level: level,
  //     notes: [],
  //     tags: [],
  //     updatedAt: new Date(),
  //     createdAt: new Date()
  //   };

  //   this.paragraphs.push(paragraph);
  //   this.renderParagraphs();
  // }

  // private renderParagraphs(): void {
  // this.onDocumentChange();;

  //   const allTags = this.paragraphs.reduce((tags: string[], paragraph) => {
  //     if (paragraph.tags && Array.isArray(paragraph.tags)) {
  //       return [...tags, ...paragraph.tags];
  //     }
  //     return tags;
  //   }, []);

  //   // Call the service to ensure we have styles for all tags
  //   this.tagColorService.ensureTagStyles(allTags);

  //   const editor = this.editorRef.nativeElement;
  //   editor.innerHTML = '';

  //   this.paragraphs.forEach((paragraph, i: number) => {
  //     // Create the outermost div (replaces the p element)
  //     const outerDiv = document.createElement('div');
  //     outerDiv.className = 'editor-row';
  //     outerDiv.id = paragraph.id;

  //     // Create nested structure with 4 levels of divs for bullets
  //     const level3 = document.createElement('div');
  //     level3.className = 'bullet';

  //     const level2 = document.createElement('div');
  //     level2.className = 'bullet';
  //     level3.appendChild(level2);

  //     const level1 = document.createElement('div');
  //     level1.className = 'bullet';
  //     level2.appendChild(level1);

  //     // This is the innermost div that will contain the actual content
  //     const contentDiv = document.createElement('div');
  //     contentDiv.className = 'bullet content-div';
  //     contentDiv.setAttribute('contenteditable', 'true');
  //     contentDiv.innerHTML = paragraph.content;
  //     level1.appendChild(contentDiv);

  //     // Apply styles from paragraph to the content div
  //     Object.assign(contentDiv.style, paragraph.styles);

  //     // Handle indentation
  //     outerDiv.style.paddingLeft = `${paragraph.level * 40}px`;

  //     // Apply tag-based classes to bullets
  //     this.applyTagClassesToBullets(paragraph.tags || [], [
  //       contentDiv,
  //       level1,
  //       level2,
  //       level3,
  //     ]); ////[level3, level2, level1, contentDiv]);

  //     // Add the nested structure to the editor
  //     outerDiv.appendChild(level3);
  //     editor.appendChild(outerDiv);

  //     // Mark this row with its type if it's a list item
  //     if (paragraph.type === 'number' || paragraph.type === 'bullet') {
  //       outerDiv.setAttribute('data-list-type', paragraph.type);
  //     }
  //   });
  // }

  // /**
  //  * Applies CSS classes to bullet elements based on the paragraph's tags
  //  * @param tags Array of tag strings from the paragraph
  //  * @param bulletElements Array of the 4 nested bullet div elements
  //  */
  // private applyTagClassesToBullets(
  //   tags: string[],
  //   bulletElements: HTMLElement[]
  // ): void {
  //   // We'll handle up to 4 tags, one for each bullet level
  //   const maxBullets = 4;

  //   // Take only the first 4 tags (if there are more)
  //   const tagsToUse = tags.slice(0, maxBullets);

  //   // Apply CSS classes to the corresponding bullet elements
  //   bulletElements.forEach((element, index) => {
  //     // First, remove any existing tag classes to avoid conflicts
  //     element.classList.forEach((className) => {
  //       if (className.startsWith('tag-')) {
  //         element.classList.remove(className);
  //       }
  //     });

  //     // If we have a tag for this bullet level, apply a class based on the tag
  //     if (index < tagsToUse.length) {
  //       const tag = tagsToUse[index];
  //       // Use the service to generate the sanitized class name
  //       const tagClass = `tag-${this.tagColorService.sanitizeTagForCssClass(
  //         tag
  //       )}`;
  //       element.classList.add(tagClass);
  //     } else {
  //       // If we don't have a tag for this bullet level, apply a default white color class
  //       element.classList.add('tag-default');
  //     }
  //   });
  // }
  
  ctrlDown = false;
  @HostListener('keydown.meta', ['$event'])
  onMeta(event: KeyboardEvent): void {
    this.manager.ctrlDown = true;
  }
  @HostListener('keyup.meta', ['$event'])
  offMeta(event: KeyboardEvent): void {
    this.manager.ctrlDown = false;
  }
  @HostListener('keydown.ctrl', ['$event'])
  onCtrl(event: KeyboardEvent): void {
    this.manager.ctrlDown = true;
  }
  @HostListener('keyup.ctrl', ['$event'])
  offCtrl(event: KeyboardEvent): void {
    this.manager.ctrlDown = false;
  }
  @HostListener('keydown.shift', ['$event'])
  onShift(event: KeyboardEvent): void {
    this.manager.shiftDown = true;
  }
  @HostListener('keyup.shift', ['$event'])
  offShift(event: KeyboardEvent): void {
    this.manager.shiftDown = false;
  }

  onInput(event: Event): void {
    this.manager.onInput(event, this.paragraphs)
    // const editor = this.editorRef.nativeElement;

    // // Handle direct text nodes
    // const childNodes = Array.from(editor.childNodes);
    // childNodes.forEach((node: any) => {
    //   if (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) {
    //     // Create the nested div structure
    //     const outerDiv = document.createElement('div');
    //     outerDiv.className = 'editor-row';
    //     outerDiv.id = crypto.randomUUID();

    //     const level3 = document.createElement('div');
    //     level3.className = 'bullet';

    //     const level2 = document.createElement('div');
    //     level2.className = 'bullet';
    //     level3.appendChild(level2);

    //     const level1 = document.createElement('div');
    //     level1.className = 'bullet';
    //     level2.appendChild(level1);

    //     const contentDiv = document.createElement('div');
    //     contentDiv.className = 'bullet content-div';
    //     contentDiv.setAttribute('contenteditable', 'true');
    //     contentDiv.textContent = node.textContent;
    //     level1.appendChild(contentDiv);

    //     // Remove the text node and add our structure
    //     node.parentNode?.removeChild(node);
    //     outerDiv.appendChild(level3);
    //     editor.insertBefore(outerDiv, editor.firstChild);

    //     // Add to our data model
    //     this.paragraphs.unshift({
    //       id: outerDiv.id,
    //       content: contentDiv.innerHTML,
    //       styles: {
    //         fontSize: '16px',
    //         textAlign: 'left',
    //         minHeight: '24px',
    //       },
    //       type: 'none',
    //       level: 0,
    //       notes: [],
    //       tags: [],
    //       updatedAt: new Date(),
    //       createdAt: new Date()
    //     });
    //   }
    // });

    // this.updateParagraphContent();
  }
  
  @HostListener('keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    this.manager.onKeyDown(this.paragraphs, event);
    // if (event.key === 'Enter') {
    //   event.preventDefault();

    //   const selection = window.getSelection();
    //   if (!selection) return;

    //   const range = selection.getRangeAt(0);
    //   let currentNode = range.commonAncestorContainer;

    //   // Find the containing editor row
    //   let editorRow = null;
    //   let node = currentNode;
    //   while (node && !editorRow) {
    //     if (
    //       node.nodeType === Node.ELEMENT_NODE &&
    //       (node as HTMLElement).classList.contains('editor-row')
    //     ) {
    //       editorRow = node;
    //       break;
    //     }
    //     node = node.parentNode!;
    //   }

    //   if (!editorRow) return;
    //   const currentParagraph = editorRow as HTMLElement;

    //   const currentIndex = this.paragraphs.findIndex(
    //     (p) => p.id === currentParagraph.id
    //   );
    //   if (currentIndex === -1) return;

    //   // Get content from the content div
    //   const contentDiv = currentParagraph.querySelector('.content-div');
    //   const currentContent = contentDiv ? contentDiv.innerHTML : '';

    //   // Check if we're at the end of an empty paragraph
    //   const isEmptyParagraph =
    //     currentContent.trim() === '' || currentContent === '<br>';

    //   // If Ctrl/Meta key is pressed, insert a line break instead of creating a new paragraph
    //   if (this.ctrlDown) {
    //     // Insert a line break at the current cursor position
    //     const br = document.createElement('br');
    //     range.deleteContents();
    //     range.insertNode(br);
        
    //     // Move the cursor after the inserted line break
    //     range.setStartAfter(br);
    //     range.collapse(true);
    //     selection.removeAllRanges();
    //     selection.addRange(range);
        
    //     // Update the paragraph content in your data model
    //     if (contentDiv) {
    //       this.paragraphs[currentIndex].content = contentDiv.innerHTML;
    //     }
    //   this.onDocumentChange();;
    //     return;
    //   }

    //   // If it's an empty list item, convert it to a regular paragraph
    //   // if (isEmptyParagraph && this.paragraphs[currentIndex].type !== 'none') {
    //   //   this.paragraphs[currentIndex].type = 'none';
    //   //   this.paragraphs[currentIndex].level = 0;
    //   //   this.renderParagraphs();
    //   //   return;
    //   // }

    //   // Create new paragraph with same properties
    //   const newParagraph: Paragraph = {
    //     id: crypto.randomUUID(),
    //     content: '<br>', // Start with empty content
    //     styles: { ...this.paragraphs[currentIndex].styles },
    //     type: this.paragraphs[currentIndex].type, // Maintain the list type
    //     level: this.paragraphs[currentIndex].level, // Maintain the indentation level
    //     notes: this.paragraphs[currentIndex].notes,
    //     tags: this.paragraphs[currentIndex].tags,
    //     updatedAt: this.paragraphs[currentIndex].updatedAt,
    //     createdAt: this.paragraphs[currentIndex].createdAt
    //   };

    //   // Insert new paragraph
    //   this.paragraphs.splice(currentIndex + 1, 0, newParagraph);
    //   this.renderParagraphs();

    //   this.selectedParagraphId = newParagraph.id;

    //   // Set cursor position to new paragraph's content div
    //   setTimeout(() => {
    //     const newElement = document.getElementById(newParagraph.id);
    //     if (newElement) {
    //       const contentDiv = newElement.querySelector('.content-div');
    //       if (contentDiv) {
    //         const range = document.createRange();
    //         range.setStart(contentDiv, 0);
    //         range.collapse(true);

    //         const selection = window.getSelection();
    //         if (selection) {
    //           selection.removeAllRanges();
    //           selection.addRange(range);
    //         }
    //       }
    //     }
    //   }, 0);
    // }
  }

  @HostListener('keydown.tab', ['$event'])
  onTabKey(event: KeyboardEvent): void {
    this.manager.onTabKey(this.paragraphs, event);
    // Prevent default tab behavior (which would move focus to next element)
    // event.preventDefault();
    
    // // Handle the tab insertion
    // this.insertTabAtCursor(event.shiftKey);
  }
  // private insertTabAtCursor(isShiftTab: boolean = false): void {
  //   const selection = window.getSelection();
  //   if (!selection) return;
    
  //   const range = selection.getRangeAt(0);
  //   let currentNode = range.commonAncestorContainer;
  
  //   // Find the containing editor row
  //   let editorRow = null;
  //   let node = currentNode;
  //   while (node && !editorRow) {
  //     if (
  //       node.nodeType === Node.ELEMENT_NODE &&
  //       (node as HTMLElement).classList.contains('editor-row')
  //     ) {
  //       editorRow = node;
  //       break;
  //     }
  //     node = node.parentNode!;
  //   }
  
  //   if (!editorRow) return;
  //   const currentParagraph = editorRow as HTMLElement;
  
  //   // Find the corresponding paragraph in our data model
  //   const currentIndex = this.paragraphs.findIndex(
  //     (p) => p.id === currentParagraph.id
  //   );
  //   if (currentIndex === -1) return;
  
  //   // Get content div
  //   const contentDiv = currentParagraph.querySelector('.content-div');
  //   if (!contentDiv) return;
  
  //   this.insertTabCharacter(range, selection);
  
  //   // Update paragraph content in data model
  //   this.paragraphs[currentIndex].content = contentDiv.innerHTML;
  // this.onDocumentChange();;
  // }
  // /**
  //  * Inserts a tab character (4 spaces) at the cursor position
  //  */
  // private insertTabCharacter(range: Range, selection: Selection): void {
  //   // Create a text node with 4 non-breaking spaces (equivalent to a tab)
  //   const tabSpaces = document.createTextNode('\u00A0\u00A0\u00A0\u00A0');
    
  //   // Insert at cursor position
  //   range.deleteContents();
  //   range.insertNode(tabSpaces);
    
  //   // Move cursor after the inserted tab
  //   range.setStartAfter(tabSpaces);
  //   range.collapse(true);
  //   selection.removeAllRanges();
  //   selection.addRange(range);
  // }

  onEditorClick(event: MouseEvent): void {
    this.manager.onEditorClick(this.paragraphs, event);
    // const target = event.target as HTMLElement;
    // let editorRow = target.closest('.editor-row');

    // if (editorRow) {
    //   this.selectParagraph(editorRow.id);
    // }
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
  //   } else {
  //     this.selectedParagraphIds = [id];
  //   }

  //   this.editorRef.nativeElement
  //     .querySelectorAll('.editor-row')
  //     .forEach((row: HTMLElement) => {
  //       row.classList.remove('selected');
  //     });

  //   const selectedElement = document.getElementById(id);
  //   if (selectedElement) {
  //     selectedElement.classList.add('selected');
  //   }

  //   if (this.selectedParagraphIds.length > 0) {
  //     this.paragraphs.forEach((p) => {
  //       const rowEl = document.getElementById(p.id);
  //       if (this.selectedParagraphIds?.includes(p.id)) {
  //         if (rowEl) {
  //           rowEl.classList.add('grouped');
  //         }
  //       } else {
  //         if (rowEl) {
  //           rowEl.classList.remove('grouped');
  //         }
  //       }
  //     });
  //   }
  // }
  // showNoteEditor = false;
  // editingNote: ParagraphNote | null = null;
  public handlePaste(event: ClipboardEvent) {
    this.manager.handlePaste(event, this.paragraphs)
    // Prevent default paste behavior
    // event.preventDefault();
  
    // // Get the pasted text content
    // const pastedText = event.clipboardData?.getData('text') || '';
  
    // // Check if the content appears to be code
    // const isLikelyCode = this.isCodeContent(pastedText);
  
    // let currentIndex = this.paragraphs.length - 1;
    // if (this.selectedParagraphId) {
    //   currentIndex = this.paragraphs.findIndex(
    //     (p) => p.id === this.selectedParagraphId
    //   );
    // }
  
    // if (isLikelyCode) {
    //   // Handle as code - create a single div with all content
    //   const newParagraph: Paragraph = {
    //     id: crypto.randomUUID(),
    //     content: pastedText, // Keep all content together
    //     styles: { 
    //       ...this.paragraphs[currentIndex].styles,
    //       fontFamily: 'monospace', // Apply code styling
    //       whiteSpace: 'pre'        // Preserve whitespace
    //     },
    //     type: 'code', // Mark this as code type
    //     level: this.paragraphs[currentIndex].level,
    //     notes: this.paragraphs[currentIndex].notes,
    //     tags: [...(this.paragraphs[currentIndex].tags || [])],
    //     updatedAt: this.paragraphs[currentIndex].updatedAt,
    //     createdAt: this.paragraphs[currentIndex].createdAt
    //   };
  
    //   // Insert the code paragraph
    //   this.paragraphs.splice(currentIndex + 1, 0, newParagraph);
    // } else {
    //   // Handle as regular text - split by newlines as before
    //   const lines = pastedText
    //     .split(/\r?\n/)
    //     .filter((line) => line.trim().length > 0); // Remove empty lines
  
    //   // Create new paragraphs for each line
    //   lines.forEach((line, i) => {
    //     const newParagraph: Paragraph = {
    //       id: crypto.randomUUID(),
    //       content: line,
    //       styles: { ...this.paragraphs[currentIndex].styles },
    //       type: this.paragraphs[currentIndex].type,
    //       level: this.paragraphs[currentIndex].level,
    //       notes: this.paragraphs[currentIndex].notes,
    //       tags: this.paragraphs[currentIndex].tags,
    //       updatedAt: new Date(),
    //       createdAt: new Date()
    //     };
  
    //     // Insert new paragraph
    //     this.paragraphs.splice(currentIndex + 1 + i, 0, newParagraph);
    //   });
    // }
  
    // this.renderParagraphs();
    
    // // Clear the paste area
    // if (event.target instanceof HTMLElement) {
    //   event.target.textContent = '';
    // }
  }
  
  // Helper method to detect if content is likely code
  // private isCodeContent(text: string): boolean {
  //   // Various heuristics to detect code:
    
  //   // 1. Check for common code patterns
  //   const codePatterns = [
  //     /[{}\[\]();][\s\S]*[{}\[\]();]/,      // Contains brackets, parentheses, etc.
  //     /\b(function|const|let|var|if|for|while|class|import|export)\b/, // Common keywords
  //     /^\s*[a-zA-Z0-9_$]+\s*\([^)]*\)\s*{/m, // Function definition pattern
  //     /^\s*import\s+.*\s+from\s+['"][^'"]+['"];?\s*$/m, // Import statement
  //     /^\s*<[a-zA-Z][^>]*>[\s\S]*<\/[a-zA-Z][^>]*>\s*$/m, // HTML-like tags
  //     /\$\{.*\}/,                           // Template literals
  //     /\b(public|private|protected)\b.*\(/  // Method definitions
  //   ];
  
  //   // 2. Check for consistent indentation (code usually has structured indentation)
  //   const lines = text.split(/\r?\n/);
  //   const indentationPattern = lines
  //     .filter(line => line.trim().length > 0)
  //     .map(line => line.match(/^\s*/)?.[0].length || 0);
    
  //   const hasConsistentIndentation = 
  //     indentationPattern.length > 3 && 
  //     new Set(indentationPattern).size > 1 && 
  //     new Set(indentationPattern).size < indentationPattern.length / 2;
  
  //   // 3. Check for code-to-text ratio (code usually has more special characters)
  //   const specialCharsCount = (text.match(/[{}[\]();:.,<>?!&|^%*+=/\\-]/g) || []).length;
  //   const textLength = text.length;
  //   const specialCharRatio = specialCharsCount / textLength;
    
  //   // 4. Check for multi-line with specific structure
  //   const hasMultipleLines = lines.length > 2;
    
  //   // Return true if any of the code patterns are found or multiple indicators are present
  //   return (
  //     codePatterns.some(pattern => pattern.test(text)) ||
  //     (hasMultipleLines && (hasConsistentIndentation || specialCharRatio > 0.1))
  //   );
  // }
  getTags(): void {
    this.tagApi.getTags('test').subscribe(x =>
      console.log('token', x)
    );
    // this.notesApi.getNoteElements('temp').subscribe((elements) => {
    //   console.log(elements);
    // });
  }
}
