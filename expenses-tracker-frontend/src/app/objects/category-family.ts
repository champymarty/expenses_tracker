import { Category } from './category';

export interface CategoryFamily {
  id: number;
  name: string;
  regex_pattern: string;
  categories: Category[] | null;
}
