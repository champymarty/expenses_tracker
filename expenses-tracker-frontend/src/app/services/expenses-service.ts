import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Source } from '../objects/source';
import { ExpensesUpload } from '../objects/expenses-upload';
import { Expense } from '../objects/expense';

@Injectable({
  providedIn: 'root',
})
export class ExpensesService {
  private readonly apiUrl = environment.apiBaseUrl + '/expenses/';

  constructor(private http: HttpClient) {}

  getExpenses(start?: string | null, end?: string | null): Observable<any> {
    let params = new HttpParams();
    if (start) {
      params = params.set('start_date', start);
    }
    if (end) {
      params = params.set('end_date', end);
    }
    const headers = new HttpHeaders({ Accept: 'application/json' });

    return this.http.get<any>(this.apiUrl, { params, headers });
  }

  patchExpense(expense: Expense): Observable<Expense> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    });
    return this.http.patch<Expense>(`${this.apiUrl}${expense.id}`, expense, { headers });
  }

  upload_expenses(files: File[], source_id: number): Observable<ExpensesUpload> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file, file.name); // Append each file
    });

    let params = new HttpParams();
    params = params.set('source_id', source_id);

    return this.http.post<ExpensesUpload>(`${this.apiUrl}${source_id}/upload`, formData);
  }
}
