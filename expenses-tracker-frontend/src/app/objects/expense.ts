import { CategoryFamily } from './category-family';
import { Source } from './source';
import { User } from './User';

export interface Expense {
  id: number;
  date: string;
  description: string;
  amount: number;
  original_category: string;
  lock_category: number;
  calculation_status: string;

  source: Source;
  user: User;
  categoryFamily: CategoryFamily;
}
