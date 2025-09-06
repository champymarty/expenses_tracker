import { CategoryFamily } from './category-family';

export interface Category {
  id: number | null;
  name: string;
  category_family_id: number;
}
