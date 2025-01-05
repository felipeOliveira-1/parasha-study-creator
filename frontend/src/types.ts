export interface Parasha {
  name: string;
  book: string;
  reference: string;
}

export interface Study {
  summary: string;
  themes: string;
  topics: string;
  mussar_analysis?: string;
  references: any[];
  generated_at: string;
}
