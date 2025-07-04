import { Injectable } from '@angular/core';
import { Paragraph } from '../types/note';

export type TextDecoration = 'bold' | 'underline' | 'strike' | 'italic' | 'large'; // 'line-through';

@Injectable({
    providedIn: 'root',
})
export class ItemStyleMangerService {
    // Rich-text helper

    /* ------------- internal helper --------------------------------- */
    /** Insert an invisible boundary marker at the start or end of `range`
     *  and return it. */
    private insertMarker(range: Range, atStart: boolean): HTMLSpanElement {
        const m = document.createElement('span');
        m.className = 'rt-sel-marker';
        m.style.cssText = 'display:inline-block;width:0;height:0;overflow:hidden';
        const clone = range.cloneRange();
        clone.collapse(atStart);
        clone.insertNode(m);
        return m;
    }

    /** If a text node is only PARTLY in the range, split it so that
     *  the chunk we return lies COMPLETELY inside the range. */
    private isolateForRange(node: Text, range: Range): Text {
        // Split at the range start
        if (node === range.startContainer && range.startOffset > 0) {
            node = node.splitText(range.startOffset);
        }
        // Split at the range end
        if (node === range.endContainer && range.endOffset < node.length) {
            node.splitText(range.endOffset);
        }
        return node;
    }
    /** Find the nearest ancestor `<span>` whose *own* classList
     *  contains the decoration we care about. Returns `null`
     *  when the text has no such wrapper.                        */
    private closestDecorated(node: Node, className: string): HTMLSpanElement | null {
        let el: Node | null = node.parentNode;
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            const e = el as HTMLElement;
            if (e.classList.contains(className)) return e as HTMLSpanElement;
            el = el.parentNode;
        }
        return null;
    }

    /** Remove `className` decoration *from exactly this text node*
     *  (or any ancestor it sits in) without touching the same
     *  decoration that lies outside the current selection.      */
    /* ---------- NEW: surgical un-wrapper ---------------------------- */

    private removeDecorationFromNode(node: Text, cls: string): void {
        const wrapper = this.closestDecorated(node, cls);
        if (!wrapper) return;

        /* STEP 1 ─ tighten every ancestor between `node` and `wrapper`
       so that `branch` ends as a *direct* child of `wrapper`
       and contains *only* the selected characters. */
        let branch: Node = node;

        while (branch.parentNode !== wrapper) {
            const parent = branch.parentNode as HTMLElement;

            /* Split the parent element into [before][branch][after]        */
            const before = document.createDocumentFragment();
            while (parent.firstChild && parent.firstChild !== branch) {
                before.appendChild(parent.firstChild);
            }
            const after = document.createDocumentFragment();
            while (branch.nextSibling) {
                after.appendChild(branch.nextSibling);
            }

            if (before.childNodes.length) {
                const leftClone = parent.cloneNode(false) as HTMLElement;
                leftClone.appendChild(before);
                parent.parentNode!.insertBefore(leftClone, parent);
            }
            if (after.childNodes.length) {
                const rightClone = parent.cloneNode(false) as HTMLElement;
                rightClone.appendChild(after);
                parent.parentNode!.insertBefore(rightClone, parent.nextSibling);
            }

            /* Now `parent` contains only `branch`; climb one level up. */
            branch = parent;
        }

        /* STEP 2 ─ split the *wrapper* itself into [before][branch][after],
       then replace it with `branch` (thus removing `cls` *only for
       the selected slice*).                                         */
        const host = wrapper.parentNode!;
        const beforeW = document.createDocumentFragment();
        while (wrapper.firstChild && wrapper.firstChild !== branch) {
            beforeW.appendChild(wrapper.firstChild);
        }
        const afterW = document.createDocumentFragment();
        while (branch.nextSibling) {
            afterW.appendChild(branch.nextSibling);
        }

        if (beforeW.childNodes.length) {
            const leftWrapper = wrapper.cloneNode(false) as HTMLElement;
            leftWrapper.appendChild(beforeW);
            host.insertBefore(leftWrapper, wrapper);
        }
        if (afterW.childNodes.length) {
            const rightWrapper = wrapper.cloneNode(false) as HTMLElement;
            rightWrapper.appendChild(afterW);
            host.insertBefore(rightWrapper, wrapper.nextSibling);
        }

        wrapper.replaceWith(branch); // bold/underline/strike gone for *exact* slice
    }

    /* ------------- public API -------------------------------------- */

    /** Toggle a style class (bold / underline / strike) ON or OFF
     *  for exactly the characters currently selected.
     *  - Works across multiple <div> paragraphs
     *  - Allows stacked styles on the same text
     *  - Splits boundary text nodes so styling never bleeds  */

    // This only works if muliple lines are selected and if there is already a style, it doesn't split it up with a new style, it just adds the style to the parent
    public toggleDecoration(decoration: TextDecoration): Range | null {
        // const decoration = decoration1 === 'bold' ? 'bold' : decoration1 === 'underline' ? 'underline' : 'strike';

        const sel = window.getSelection();
        if (!sel?.rangeCount) return null;

        const range = sel.getRangeAt(0);
        if (range.collapsed) return null;

        const className = `rt-${decoration}`;

        /* STEP 0 – snapshot the nodes we’ll modify *before* touching the DOM */
        const textNodes: Text[] = [];
        const root = range.commonAncestorContainer;

        if (root.nodeType === Node.TEXT_NODE && range.intersectsNode(root)) {
            textNodes.push(this.isolateForRange(root as Text, range));
        }

        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                if (!node.textContent?.trim()) return NodeFilter.FILTER_REJECT;
                const nr = document.createRange();
                nr.selectNodeContents(node);
                return range.compareBoundaryPoints(Range.END_TO_START, nr) < 0 && range.compareBoundaryPoints(Range.START_TO_END, nr) > 0
                    ? NodeFilter.FILTER_ACCEPT
                    : NodeFilter.FILTER_REJECT;
            },
        });
        while (walker.nextNode()) {
            textNodes.push(this.isolateForRange(walker.currentNode as Text, range));
        }
        if (!textNodes.length) return null;

        /* STEP 1 – drop invisible boundary markers so we can restore
              the user’s highlight after DOM surgery. */
        const startMarker = this.insertMarker(range, true);
        const endMarker = this.insertMarker(range, false);

        /* STEP 2 – decide add vs remove and mutate the DOM */
        const allStyled = textNodes.every(t => this.closestDecorated(t, className));

        if (allStyled) {
            textNodes.forEach(t => this.removeDecorationFromNode(t, className));
        } else {
            textNodes.forEach(t => {
                if (this.closestDecorated(t, className)) return;
                const span = document.createElement('span');
                span.classList.add(className);
                t.replaceWith(span);
                span.appendChild(t);
            });
        }

        /* STEP 3 – restore the exact selection, then clean up markers */
        const newRange = document.createRange();
        newRange.setStartAfter(startMarker);
        newRange.setEndBefore(endMarker);

        sel.removeAllRanges();
        sel.addRange(newRange);

        startMarker.remove();
        endMarker.remove();

        return newRange;
    }
}
