import { FileFailedToExtract } from './file-failed-to-extract';

export interface ExpensesUpload {
  created_expenses: number;
  existing_expenses: number;
  filesFailedToExtract: FileFailedToExtract[];
}
