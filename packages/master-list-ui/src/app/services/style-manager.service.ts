import { Injectable } from '@angular/core';
import { Paragraph } from '../types/note';

export type TextDecoration = 'bold' | 'underline' | 'line-through';

@Injectable({
    providedIn: 'root',
})
export class StyleMangerService {
    /* -----------------------------------------------------------
   Rich-text helper  |  src/app/shared/rich-text.util.ts
   ----------------------------------------------------------- */

    /** Styles you currently support. Add more when needed. */

    /* ------------- internal helper --------------------------------- */
    /** Insert an invisible boundary marker at the start or end of `range`
     *  and return it. */
    insertMarker(range: Range, atStart: boolean): HTMLSpanElement {
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
    isolateForRange(node: Text, range: Range): Text {
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
    closestDecorated(node: Node, className: string): HTMLSpanElement | null {
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
    removeDecorationFromNode(node: Text, className: string): void {
        const wrapper = this.closestDecorated(node, className);
        if (!wrapper) return;

        /* Find the wrapper’s *direct* child that contains `node`
       (handles the nested-span case). */
        let branch: Node = node;
        while (branch.parentNode !== wrapper) branch = branch.parentNode!;

        const parent = wrapper.parentNode!;
        const before = document.createDocumentFragment();
        const after = document.createDocumentFragment();

        /* Move siblings *before* the branch into `before`. */
        while (wrapper.firstChild && wrapper.firstChild !== branch) {
            before.appendChild(wrapper.firstChild);
        }

        /* Move siblings *after* the branch into `after`. */
        while (branch.nextSibling) {
            after.appendChild(branch.nextSibling);
        }

        /* Re-wrap the preserved parts so they keep the decoration. */
        if (before.childNodes.length) {
            const leftSpan = wrapper.cloneNode(false) as HTMLElement;
            leftSpan.appendChild(before);
            parent.insertBefore(leftSpan, wrapper);
        }
        if (after.childNodes.length) {
            const rightSpan = wrapper.cloneNode(false) as HTMLElement;
            rightSpan.appendChild(after);
            parent.insertBefore(rightSpan, wrapper.nextSibling);
        }

        /* Finally, replace the *whole* wrapper with the branch
       (which still contains `node` and any nested styles). */
        wrapper.replaceWith(branch);
    }

    /* ------------- public API -------------------------------------- */

    /** Toggle a style class (bold / underline / strike) ON or OFF
     *  for exactly the characters currently selected.
     *  - Works across multiple <div> paragraphs
     *  - Allows stacked styles on the same text
     *  - Splits boundary text nodes so styling never bleeds  */

    // This only works if muliple lines are selected and if there is already a style, it doesn't split it up with a new style, it just adds the style to the parent
    toggleDecoration(decoration1: TextDecoration): Range | null{
        const decoration = decoration1 === 'bold' ? 'bold' : decoration1 === 'underline' ? 'underline' : 'strike';

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
