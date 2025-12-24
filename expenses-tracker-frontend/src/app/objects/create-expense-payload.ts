export interface CreateExpensePayload {
  description: string;
  amount: number;
  date: string;
  category_name: string;
  sourceId: number;
}
