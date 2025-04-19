import { CommonModule } from '@angular/common';
import {
    Component,
    ElementRef,
    HostListener,
    ViewChild,
    ViewEncapsulation,
} from '@angular/core';
import { Paragraph } from '../../types/note';
import {  } from '../meta-tags/meta-tag.service';
import { MetaTagsComponent } from '../meta-tags/meta-tags.component';
import { NotesApiService } from '../../services/notes-api.service';
import { TagCssGenerator } from '../../services/tag-css-generator';
import { BehaviorSubject, debounceTime, skip, Subject, tap } from 'rxjs';
import { TagDelete, TagSelection, TagSelectionGroup } from '../../types/tag';
import { TagApiService } from '../../services/tag-api';
import { ToastrService } from 'ngx-toastr';
import { MasterLayoutService } from '../master-layout/master-layout.service';
import { AuthCoreService } from '@master-list/auth';
import { TagUpdate } from '../../types/tag/tag-update';
import { AddTag } from '../tag-group/tag-group.component';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-list-editor',
  imports: [CommonModule, MetaTagsComponent,],
  templateUrl: './list-editor.component.html',
  styleUrl: './list-editor.component.scss',
  encapsulation: ViewEncapsulation.None,
})
export class ListEditorComponent {
 @ViewChild('editor') editorRef!: ElementRef;

    tagGroup$: BehaviorSubject<TagSelectionGroup> = new BehaviorSubject<TagSelectionGroup>({ name: 'Lists', tags: [] });
    paragraphs: Paragraph[] = [];

    private changeSubject = new Subject<void>();
    private isSaving = false;
    public error = false;
    private noteId!: string;
    public popListOut = false;
    public updateDeleteName!: TagDelete;
    public updateAddName!: TagUpdate | TagUpdate[];
    public listType: 'note' | 'tag' = 'note';

    affectedRows: Paragraph[] = [];
    constructor(
        private notesApi: NotesApiService,
        private tagApi: TagApiService,
        private tagColorService: TagCssGenerator,
        private toastr: ToastrService,
        private manager: MasterLayoutService,
        private authService: AuthCoreService,
        private route: ActivatedRoute,
    ) {
        this.manager.setChangeSubject(this.changeSubject);
        this.changeSubject
            .pipe(
                debounceTime(2000), // 2 seconds of inactivity
                skip(1),
            )
            .subscribe(() => {
                this.saveNoteElements();
            });
    }

    private componentVersion = 0;

    ngOnInit() {
        this.tagApi
            .getDefaultTags()
            .pipe(tap(x => this.tagColorService.initTagColors(x)))
            .subscribe(x => this.tagGroup$.next(x));
        this.tagGroup$.subscribe();

        this.route.paramMap.subscribe(params => {
            let listId = params.get('id');
            let listType = params.get('listType');
            
            if (!listId || !listType || listType === 'note') {
                this.tagApi.getTags('my-note-test', 1, 10).subscribe(x => {
                    const found = x.data.find((y: any) => y.name === 'my-note-test');
                    console.log('found', found);
                    if (!found) {
                        this.tagApi.createTag('my-note-test').subscribe(response => {
                            this.noteId = response.data.id;
                            console.log('noteId created', this.noteId);
                            const tagUpdate = { id: response.data.order, name: response.data.name };
                            this.updateAddName = tagUpdate;
                            this.getNotes();
                        });
                    } else {
                        this.noteId = found.id;
                        console.log('noteId found', this.noteId);
                        this.getNotes();
                    }
                });
            } else {
              this.listType = (listType as 'tag' | 'note');
              this.tagApi.getTags(null, 1, 10, listId).subscribe(x => {
                const found = x.data.find((y: any) => y.id === listId);
                console.log('found', found);
                // if (!found) {
                //     this.tagApi.createTag('my-note-test').subscribe(response => {
                //         this.noteId = response.data.id;
                //         console.log('noteId created', this.noteId);
                //         const tagUpdate = { id: response.data.order, name: response.data.name };
                //         this.updateAddName = tagUpdate;
                //         this.getNotes();
                //     });
                // } else {
                if(found) {
                    this.noteId = found.id;
                    console.log('noteId found', this.noteId);
                    this.getNotes();
                } else {
                  console.error(`List with id ${listId} note found`);
                }

                // }
            });
            }

        });
    }

    getNotes() {
        
        this.notesApi.getNoteElements(this.noteId, this.listType /*'note'*/).subscribe({
            next: x => {
                console.log('getNotes', x);
                const noteElements = x.data.notes;
                const tags = x.data.tags;
                this.paragraphs = noteElements;

                // Todo: check if it is adding multiple tags
                const tagUpdates =tags.map(tag => {
                    const tagUpdate = { id: tag.order, name: tag.name };
                    // this.updateAddName = tagUpdate;
                    this.tagColorService.addTag(tag);
                    return tagUpdate;
                });
                this.updateAddName = tagUpdates;
                this.manager.ngAfterViewInit(this.editorRef, this.paragraphs);
            },
        });
    }

    ngAfterViewInit() {
        this.paragraphs = this.manager.ngAfterViewInit(this.editorRef, this.paragraphs);
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

    private updateParagraphPositions(): void {
        // Simple position update - just assign sequential numbers
        this.paragraphs.forEach((paragraph, index) => {
            paragraph.position = index;
        });
    }

    public addTag(tag: AddTag) {
        if (tag.create) {
            this.tagApi.createTag(tag.name!).subscribe(response => {
                this.tagColorService.addTag(response.data);
                console.log('add tag response', response);
                const tagUpdate = { id: response.data.order, name: response.data.name };
                this.updateAddName = tagUpdate;
            });
        } else {
            const tagUpdate = { order: tag.tag!.order, name: tag.tag!.name, id: '', parent_id: '', created_at: '' };
            this.tagColorService.addTag(tagUpdate);
        }
    }
    public deleteTag(name: string) {
        this.tagApi.deleteTag(name).subscribe(response => {
            console.log('add tag response', response);
            if (response.data) {
                this.updateDeleteName = { name };
            }
        });
    }

    public removeTag() {}

    public unassignTags(tags: string[]): void {
        this.manager.unassignTag(tags, this.paragraphs);
    }

    public assignTagToRows(tagName: string) {
        this.manager.assignTagToRows(tagName, this.paragraphs);
    }

    // Bold, italics, lineThrough click event
    public applyInlineStyle(style: string): void {
        this.manager.applyInlineStyle(style, this.paragraphs);
    }

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
        this.manager.onInput(event, this.paragraphs);
    }

    @HostListener('keydown', ['$event'])
    onKeyDown(event: KeyboardEvent): void {
        this.manager.onKeyDown(this.paragraphs, event);
    }

    @HostListener('keydown.tab', ['$event'])
    onTabKey(event: KeyboardEvent): void {
        this.manager.onTabKey(this.paragraphs, event);
    }

    onEditorClick(event: MouseEvent): void {
        this.manager.onEditorClick(this.paragraphs, event);
    }

    public handlePaste(event: ClipboardEvent) {
        this.manager.handlePaste(event, this.paragraphs);
    }

    public saveNoteElements(overrideError: boolean = false): void {
        if (!this.isSaving && (!this.error || overrideError)) {
            this.isSaving = true;
            this.updateParagraphPositions();
            this.notesApi.saveNoteElements(this.paragraphs, this.noteId, this.listType).subscribe({
                next: result => {
                        this.isSaving = false;
                },
                error: result => {
                    this.error = true;
                    this.isSaving = false;
                    this.toastr.error('Note not saved', 'Error');
                },
            });
        }
    }
}
