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
import { TagDelete, TagSelection, TagSelectionGroup } from '../../types/tag';
import { TagApiService } from '../../services/tag-api';
import { ToastrService } from 'ngx-toastr';
import { MasterLayoutService } from './master-layout.service';
import { NavListComponent } from '../nav-list/nav-list.component';
import { MsalService } from '@azure/msal-angular';
import { AuthCoreService } from '@master-list/auth';
import { TagUpdate } from '../../types/tag/tag-update';
import { AddTag } from '../tag-group/tag-group.component';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-master-layout',
    imports: [
        CommonModule,
        MetaTagsComponent,
        NavListComponent,
    ],
    templateUrl: './master-layout.component.html',
    styleUrl: './master-layout.component.scss',
    encapsulation: ViewEncapsulation.None,
})

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

    tagGroup$: BehaviorSubject<TagSelectionGroup> = new BehaviorSubject<TagSelectionGroup>({ name: 'Lists', tags: [] });
    paragraphs: Paragraph[] = [];
  

    private changeSubject = new Subject<void>();
    private isSaving = false;
    public error = false;
    private noteId!: string;
    public popListOut = false;
    public updateDeleteName!: TagDelete;
    public updateAddName!: TagUpdate;

    affectedRows: Paragraph[] = [];
    constructor(
        private notesApi: NotesApiService,
        private tagApi: TagApiService,
        private tagColorService: TagCssGenerator,
        private toastr: ToastrService,
        private manager: MasterLayoutService,
        private authService: AuthCoreService,
        private route: ActivatedRoute
    ) {
        // private destroyRef: DestroyRef
        this.manager.setChangeSubject(this.changeSubject);
        this.changeSubject
            .pipe(
                debounceTime(2000), // 2 seconds of inactivity
                skip(1),
            )
            .subscribe(() => {
                this.saveNoteElements();
                // if (/*this.isDirty &&*/ !this.isSaving && !this.error) {
                //     // this.isDirty = false;

                //     this.isSaving = true;
                //     this.updateParagraphPositions();
                //     this.notesApi.saveNoteElements(this.paragraphs, this.noteId).subscribe({
                //         next: result => {
                //             if (result.message === 'success') {
                //                 this.isSaving = false;
                //             }
                //         },
                //         error: result => {
                //             this.error = true;
                //             this.isSaving = false;
                //             this.toastr.error('Note not saved', 'Error');
                //         },
                //     });
                // }
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
        this.tagApi
            .getLists()
            .pipe(tap(x => this.tagColorService.initTagColors(x)))
            .subscribe(x => this.tagGroup$.next(x));
        this.tagGroup$.subscribe();

        this.route.paramMap.subscribe(params => {
            let noteId = params.get('id');
            
            // Set to a random guid for now
            // this.noteId = noteId ? noteId : 'a0c1b2d3-e4f5-6789-abcd-ef0123456789';
            this.noteId = noteId ? noteId : 'a0c1b2d3-e4f5-6789-abcd-ef0123456789';
            console.log('noteId', this.noteId);
            this.notesApi
                .getNoteElements(this.noteId).subscribe({
                    next: x => {
                        // this.paragraphs = x;
                        // this.manager.initParagraphs(this.paragraphs);
                        // this.manager.setParagraphs(this.paragraphs);
                    }});
            //     .pipe(tap(x => this.tagColorService.initTagColors(x)))
            //     .subscribe(x => {
            //         this.paragraphs = x;
            //         this.manager.initParagraphs(this.paragraphs);
            //         this.manager.setParagraphs(this.paragraphs);
            //         this.manager.setEditorRef(this.editorRef);
            //         this.manager.setTagGroup(this.tagGroup$);
            //         this.manager.setNoteId(this.noteId);
            //         this.manager.setTagColorService(this.tagColorService);
            //         this.manager.setParagraphNote({
            //             paragraphs: this.paragraphs,
            // noteId =
          })
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
                this.updateAddName = response.data;
            });
        } else {
            const tagUpdate = { id: tag.tag!.order, name: tag.tag!.name };
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
    
    public saveNoteElements(): void {
        // this.tagApi.getTags('test').subscribe(x => console.log('token', x));
        if (!this.isSaving && !this.error) {
            this.isSaving = true;
            this.updateParagraphPositions();
            this.notesApi.saveNoteElements(this.paragraphs, this.noteId).subscribe({
                next: result => {
                    if (result.message === 'success') {
                        this.isSaving = false;
                    }
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
