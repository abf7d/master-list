export interface NoteItemTag {
  id: string | null;
  name: string;
  sort_order: number | null;
  page?: number | null;
}
export interface Paragraph {
  id: string;
  content: string;
  tags: NoteItemTag[];
  createdAt: Date;
  updatedAt: Date;
  position?: number;
  creation_list_id: string | null;
  creation_type: 'note' | 'tag' | null;
  origin_sort_order?: number;
  origin_page?: number | null;
}

export interface MoveParagraphs {
  filtered: Paragraph[];
  moved: Paragraph[];
}