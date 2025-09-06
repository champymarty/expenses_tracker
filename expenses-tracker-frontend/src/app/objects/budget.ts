import { CategoryFamily } from './category-family';

export interface Budget {
  id: number | null; // Use null for new budgets
  frequency_type: number;
  target_amount: number;
  category_family: CategoryFamily;
}
