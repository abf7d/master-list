// Current Proof of Concept
export interface ParagraphNote {
  id: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface NoteItemTag {
  id: string | null;
  name: string;
  sort_order: number | null;
}
//Current Proof of Concept
export interface Paragraph {
  id: string;
  content: string;
  styles: {
    fontSize?: string;
    fontWeight?: string;
    color?: string;
    textAlign?: string;
    minHeight?: string;
    fontFamily?: string;
    whiteSpace?: string;
  };
  type: 'bullet' | 'number' | 'none' | 'code';
  level: number; // Indentation level
  tags: NoteItemTag[]; // string[];
  notes: ParagraphNote[];
  createdAt: Date;
  updatedAt: Date;
  position?: number;
  creation_list_id: string | null;
  creation_type: 'note' | 'tag' | null;
  origin_sort_order?: number;
}


// New Design
// 1. Note Element Interface
export interface NoteElement {
  id: string;          // GUID for the element
  type: 'paragraph' | 'heading' | 'list' | 'code' | 'image';  // Element type
  content: string;     // Actual content
  tags: string[];      // Tags associated with this element
  timestamp: number;   // Last modification time
  noteId: string;      // Parent note ID
  order: number;       // Position in the note
  isModified: boolean; // Flag for unsaved changes
}

// 2. Note Interface
export interface Note {
  id: string;           // GUID for the note
  title: string;        // Note title
  elements: string[];   // Array of element IDs in order
  tags: string[];       // Tags for the entire note
  created: number;      // Creation timestamp
  lastModified: number; // Last modification timestamp
}