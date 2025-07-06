import { CommonModule } from '@angular/common';
import { Component, ElementRef, HostListener, ViewChild, ViewEncapsulation } from '@angular/core';
import { NoteItemTag, Paragraph } from '../../types/note';
import { NoteApiService } from '../../services/api/note-api.service';
import { TagColorManager } from '../../services/tag-color-manager';
import { BehaviorSubject, debounceTime, skip, Subject, takeUntil, tap } from 'rxjs';
import { TagDelete, TagSelection, TagSelectionGroup } from '../../types/tag';
import { TagApiService } from '../../services/api/tag-api';
import { ToastrService } from 'ngx-toastr';
import { ListManagerService } from './list.manager';
import { AuthCoreService } from '@auth/auth-service/auth.service';
import { TagUpdate } from '../../types/tag/tag-update';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ColorFactoryService } from '../../services/color-factory.service';
import { TagPickerComponent } from '../tag-picker/tag-picker.component';
import { FormsModule } from '@angular/forms';
import { AutosizeDirective } from '../../directives/auto-size.directive';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';
import { TextDecoration } from '../../services/item-style-manager.service';
import { AddTag, MoveItems } from '../../types/tag/tag-picker-events';
import { ModalService } from '../confirm-dialog/modal.service';
import { OverviewApiService } from '../../services/api/overview-api.service';
import { ItemApiService } from '../../services/api/item-api.service';
import { PageApiService } from '../../services/api/page-api.service';

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
    public maxPage = 0;
    public currentPage: number | null = null;
    public pages: number[] = [];
    private hasStartedPeriodicSave = false;
    private destroy$ = new Subject<void>();

    affectedRows: Paragraph[] = [];
    constructor(
        private notesApi: NoteApiService,
        private overviewApi: OverviewApiService,
        private pageApi: PageApiService,
        private itemsApi: ItemApiService,
        private tagApi: TagApiService,
        private tagColorService: TagColorManager,
        private toastr: ToastrService,
        private manager: ListManagerService,
        private authService: AuthCoreService,
        private route: ActivatedRoute,
        private colorFactory: ColorFactoryService,
        private router: Router,
        private modal: ModalService,
    ) {
        this.loadOriginParagraph = this.manager.loadOriginParagraph;
        this.manager.setChangeSubject(this.changeSubject);
    }

    private initPeriodicSave() {
        if (this.hasStartedPeriodicSave) return;
        this.hasStartedPeriodicSave = true;

        this.changeSubject.pipe(debounceTime(2000), takeUntil(this.destroy$)).subscribe(() => {
            this.saveNoteElements();
        });
    }
    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete();
    }

    ngOnInit() {
        this.route.paramMap.subscribe(params => {
            let listId = params.get('id');
            let listType = params.get('listType');
            this.currentPage = +params.get('page')! || null;
            this.listType = listType as 'tag' | 'note';
            if (listType === 'note') {
                this.notesApi.getNotes(null, 1, 10, listId).subscribe(x => {
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
        this.overviewApi.getOverview(this.listId, this.listType, this.currentPage).subscribe({
            next: x => {
                const noteElements = x.data.notes;
                const tags = x.data.tags;
                this.maxPage = x.data.max_page;
                this.pages = Array.from({ length: this.maxPage }, (_, i) => i + 1);

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
                this.manager.resetHistory();
                this.manager.saveHistory(this.paragraphs);
            },
            error: err => {
                this.error = true;
                this.isSaving = false;
                console.error('Error fetching note elements', err);
                this.toastr.error('Error fetching note elements', 'Error');
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
            this.tagHighlightNames = this.tagHighlightNames.filter(x => x !== name);
            if (response.data) {
                this.updateDeleteName = { name };
            }
        });
    }
    public deletePage() {
        this.pageApi.deletePage(this.listId, this.listType, this.currentPage).subscribe({
            next: result => {
                this.toastr.success('Page deleted successfully', 'Success');
                if (this.currentPage === this.maxPage) [(this.currentPage = null)];
                this.getPageNoteItems();
            },
            error: result => {
                this.error = true;
                this.isSaving = false;
                console.error('error', result);
                this.toastr.error('Error deleting page', 'Error');
            },
        });
    }
    public async moveItems(event: MoveItems) {
        const movedState = this.manager.moveParagraph(this.paragraphs);
        if (!movedState.moved || movedState.moved.length === 0) {
            this.toastr.warning('No list items selected', 'No items to move');
        } else if (event.action === 'list' && !event.tagName) {
            this.toastr.warning('No list selected', 'Please select a list to move items to');
        } else {
            let message = '';
            if (event.action === 'list') {
                message = 'Are you sure you want to move the selected items to the list ' + event.tagName + '? This action cannot be undone.';
            } else if (event.action === 'page') {
                message = 'Are you sure you want to move the selected items to a new page?';
            }
            const ok = await this.modal.confirm({
                title: 'Move Items',
                message,
                okText: 'Move',
                cancelText: 'Cancel',
                maxWidth: '490px',
            });
            if (ok) {
                this.itemsApi.moveNoteItems(movedState, this.listId, this.listType, event.tagName, event.action, this.currentPage).subscribe({
                    next: result => {
                        this.maxPage = result.data.max_page;
                        this.pages = Array.from({ length: this.maxPage }, (_, i) => i + 1);
                        this.toastr.success('Items moved successfully', 'Success');
                        this.paragraphs = movedState.filtered;
                        this.manager.ngAfterViewInit(this.editorRef, this.paragraphs);
                        this.manager.resetHistory();
                    },
                    error: result => {
                        this.error = true;
                        this.isSaving = false;
                        console.error('error', result);
                        this.toastr.error('Error moving items', 'Error');
                    },
                });
            } else {
                console.log('Cancelled move items');
            }
        }
    }

    private triggerChange() {
        this.initPeriodicSave(); // Ensure the save loop is started
        this.changeSubject.next();
    }
    public removeTag() {}

    public unassignTags(tags: string[]): void {
        this.manager.unassignTag(tags, this.paragraphs);
        this.triggerChange();
    }

    public assignTagToRows(tagName: string) {
        this.tagHighlightNames = Array.from(new Set([...this.tagHighlightNames, tagName]));
        this.manager.assignTagToRows(tagName, this.paragraphs);
        this.triggerChange();
    }

    // Bold, italics, lineThrough click event
    public applyInlineStyle(style: TextDecoration): void {
        this.manager.applyInlineStyle(style, this.paragraphs);
        this.triggerChange();
    }
    public mergeNoteItems(): void {
        this.manager.mergeNoteItems(this.paragraphs);
        this.triggerChange();
    }

    public deleteList() {
        if (this.listType === 'note') {
            this.notesApi.deleteNote(this.listId).subscribe({
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

    @HostListener('keyup.meta', ['$event'])
    offMeta(event: Event): void {
        this.manager.ctrlDown = false;
    }
    @HostListener('keyup.ctrl', ['$event'])
    offCtrl(event: Event): void {
        this.manager.ctrlDown = false;
    }
    @HostListener('keydown.shift', ['$event'])
    onShift(event: Event): void {
        this.manager.shiftDown = true;
    }
    @HostListener('keyup.shift', ['$event'])
    offShift(event: Event): void {
        this.manager.shiftDown = false;
    }

    onInput(event: Event): void {
        this.manager.onInput(event, this.paragraphs);
        this.triggerChange();
    }

    @HostListener('keydown', ['$event'])
    onKeyDown(event: KeyboardEvent): void {
        event.stopPropagation();
        this.manager.onKeyDown(this.paragraphs, event);
    }

    @HostListener('keydown.tab', ['$event'])
    onTabKey(event: Event): void {
        this.manager.onTabKey(this.paragraphs, event as KeyboardEvent);
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
            this.itemsApi.saveNoteItems([], this.listId, this.listType, this.listName, this.currentPage).subscribe({
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
        this.triggerChange();
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
            this.itemsApi.saveNoteItems(this.paragraphs, this.listId, this.listType, this.listName, this.currentPage).subscribe({
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
    loadPage(page: number) {
        if (page < 0 || page > this.maxPage) {
            this.toastr.error('Invalid page number', 'Error');
            return;
        }
        this.currentPage = page;
        this.router.navigate(['/', 'lists', this.listType, this.listId, page]);
        this.getPageNoteItems();
    }
}
