export interface Note {
    id: string;
    content: string;
    createdAt: Date;
    updatedAt: Date;
  }
  
 export interface Paragraph {
    id: string;
    content: string;
    styles: {
      fontSize?: string;
      fontWeight?: string;
      color?: string;
      textAlign?: string;
      minHeight?: string;
    };
    type: 'bullet' | 'number' | 'none';
    level: number; // Indentation level
    notes: Note[];
  }