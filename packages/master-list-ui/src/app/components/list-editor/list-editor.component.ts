import { CommonModule } from '@angular/common';
import { Component, ElementRef, HostListener, ViewChild, ViewEncapsulation } from '@angular/core';
import { NoteItemTag, Paragraph } from '../../types/note';
// import {} from '../meta-tags/meta-tag.service';
// import { MetaTagsComponent } from '../meta-tags/meta-tags.component';
import { NotesApiService } from '../../services/notes-api.service';
import { TagCssGenerator } from '../../services/tag-css-generator';
import { BehaviorSubject, debounceTime, skip, Subject, tap } from 'rxjs';
import { TagDelete, TagSelection, TagSelectionGroup } from '../../types/tag';
import { TagApiService } from '../../services/tag-api';
import { ToastrService } from 'ngx-toastr';
import { MasterLayoutService } from './master-layout.service';
import { AuthCoreService } from '@master-list/auth';
import { TagUpdate } from '../../types/tag/tag-update';
// import { AddTag } from '../tag-group/tag-group.component';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ColorFactoryService } from '../../services/color-factory.service';
import { AddTag, TagPickerComponent } from '../tag-picker/tag-picker.component';
import { FormsModule } from '@angular/forms';
import { AutosizeDirective } from '../../directives/auto-size.directive';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';

@Component({
    selector: 'app-list-editor',
    imports: [CommonModule, RouterModule, TagPickerComponent, FormsModule, AutosizeDirective, ClickOutsideDirective],
    templateUrl: './list-editor.component.html',
    styleUrl: './list-editor.component.scss',
    encapsulation: ViewEncapsulation.None,
})
export class ListEditorComponent {
    @ViewChild('editor') editorRef!: ElementRef;
    tags: TagSelection[] = [];
    paragraphs: Paragraph[] = [];

    private changeSubject = new Subject<void>();
    private isSaving = false;
    public error = false;
    private listId!: string;
    public popListOut = false;
    public updateDeleteName!: TagDelete;
    public updateAddName!: TagUpdate | TagUpdate[];
    public listType: 'note' | 'tag' = 'note';
    public loadOriginParagraph!: BehaviorSubject<Paragraph | null>;
    public listName: string = ''; //'Untitled';
    public listColor: string | null = null;
    public showExtraMenu = false;
    public tagHighlightNames: string[] = [];

    affectedRows: Paragraph[] = [];
    constructor(
        private notesApi: NotesApiService,
        private tagApi: TagApiService,
        private tagColorService: TagCssGenerator,
        private toastr: ToastrService,
        private manager: MasterLayoutService,
        private authService: AuthCoreService,
        private route: ActivatedRoute,
        private colorFactory: ColorFactoryService,
        private router: Router,
    ) {
        this.loadOriginParagraph = this.manager.loadOriginParagraph;
        this.manager.setChangeSubject(this.changeSubject);
        this.initPeriodicSave();
    }

    initPeriodicSave() {
        this.changeSubject
            .pipe(
                debounceTime(2000), // 2 seconds of inactivity
                skip(1),
            )
            .subscribe(() => {
                this.saveNoteElements();
            });
    }

    ngOnInit() {
        this.route.paramMap.subscribe(params => {
            let listId = params.get('id');
            let listType = params.get('listType');
            this.listType = listType as 'tag' | 'note';
            if (listType === 'note') {
                this.tagApi.getNotes(null, 1, 10, listId).subscribe(x => {
                    const found = x.data.find((y: any) => y.id === listId);
                    if (found) {
                        this.listId = found.id;
                        this.getPageNoteItems();
                    } else {
                        console.error(`List with id ${listId} note found`);
                    }
                });
            } else if (listType === 'tag') {
                this.tagApi.getTags(null, 1, 10, listId).subscribe(x => {
                    const found = x.data.find((y: any) => y.id === listId);
                    if (found) {
                        this.listId = found.id;
                        console.log('noteId found', this.listId);
                        this.getPageNoteItems();
                    } else {
                        console.error(`List with id ${listId} note found`);
                    }
                });
            }
        });
    }

    getPageNoteItems() {
        this.tagHighlightNames = [];
        this.notesApi.getNoteElements(this.listId, this.listType /*'note'*/).subscribe({
            next: x => {
                console.log('getNotes', x);
                const noteElements = x.data.notes;
                const tags = x.data.tags;
                
                this.paragraphs = noteElements;

                // Todo: check if it is adding multiple tags
                const tagUpdates = tags.map(tag => {
                    const tagUpdate = { id: tag.order, name: tag.name, navId: tag.id };
                    this.tagHighlightNames.push(tag.name);
                    this.tagColorService.addTag(tag);
                    return tagUpdate;
                });
                this.updateAddName = tagUpdates;
                this.manager.ngAfterViewInit(this.editorRef, this.paragraphs);
                this.listName = x.data.list_name;
                if (x.data.list_type === 'tag' && x.data.color_order !== null) {
                    const color = this.colorFactory.getColor(x.data.color_order);
                    this.listColor = color.backgroundcolor;
                } else {
                    this.listColor = null;
                }
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
                this.tagHighlightNames = Array.from(new Set([...this.tagHighlightNames, response.data.name]));
                const tagUpdate = { id: response.data.order, name: response.data.name, navId: response.data.id };
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
            this.tagHighlightNames = this.tagHighlightNames.filter(x => x !== name);
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
        this.tagHighlightNames = Array.from(new Set([...this.tagHighlightNames, tagName]));
        this.manager.assignTagToRows(tagName, this.paragraphs);
    }

    // Bold, italics, lineThrough click event
    public applyInlineStyle(style: string): void {
        this.manager.applyInlineStyle(style, this.paragraphs);
    }

    public deleteList() {
        if (this.listType === 'note') {
            this.tagApi.deleteNote(this.listId).subscribe({
                next: result => {
                    this.toastr.success('Note deleted', 'Success');
                    this.router.navigate(['/', 'lists']);
                },
                error: result => {
                    this.error = true;
                    this.isSaving = false;
                    this.toastr.error('Error deleting Note', 'Error');
                },
            });
        } else if (this.listType === 'tag') {
            this.tagApi.deleteTag(this.listName).subscribe({
                next: result => {
                    this.toastr.success('Tag deleted', 'Success');
                    this.router.navigate(['/', 'lists']);
                },
                error: result => {
                    this.error = true;
                    this.isSaving = false;
                    this.toastr.error('Error deleting Tag', 'Error');
                },
            });
        }
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
    public cutNoteItems() {
        this.paragraphs = this.manager.cutNoteItems(this.paragraphs);
    }
    public pasteNoteItems() {
        this.paragraphs = this.manager.pasteNoteItems(this.paragraphs);
    }

    public clearList(overrideError: boolean = false) {
        if (!this.isSaving && (!this.error || overrideError)) {
            this.isSaving = true;
            this.updateParagraphPositions();
            this.notesApi.saveNoteElements([], this.listId, this.listType, this.listName).subscribe({
                next: result => {
                    this.paragraphs = [];
                    this.isSaving = false;
                    this.manager.ngAfterViewInit(this.editorRef, this.paragraphs);
                },
                error: result => {
                    this.error = true;
                    this.isSaving = false;
                    this.toastr.error('Note not saved', 'Error');
                },
            });
        }
    }

    public saveNoteElements(overrideError: boolean = false): void {
        if (!this.isSaving && (!this.error || overrideError)) {
            this.isSaving = true;
            if (!this.listName || this.listName.trim().length === 0) {
                const p = this.paragraphs.find(x => x.content.trim().length > 0);
                if (p) {
                    this.listName = p.content.substring(0, 240).replace(/<[^>]*>/g, '');
                }
            }
            this.updateParagraphPositions();
            this.notesApi.saveNoteElements(this.paragraphs, this.listId, this.listType, this.listName).subscribe({
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
