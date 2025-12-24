import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AverageBudgetPayload } from '../objects/average-budget-payload';
import { Budget } from '../objects/budget';

@Injectable({
  providedIn: 'root',
})
export class BudgetService {
  private readonly apiUrl = environment.apiBaseUrl + '/budget';

  constructor(private http: HttpClient) {}

  getBudgetCalculations(
    start?: string | null,
    end?: string | null,
  ): Observable<AverageBudgetPayload> {
    let params = new HttpParams();
    if (start) {
      params = params.set('start_date', start);
    }
    if (end) {
      params = params.set('end_date', end);
    }
    const headers = new HttpHeaders({ Accept: 'application/json' });

    return this.http.get<AverageBudgetPayload>(this.apiUrl + '/calculate', { params, headers });
  }

  createBudget(budget: Budget): Observable<Budget> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    });
    return this.http.post<Budget>(this.apiUrl, budget, { headers });
  }

  deleteBudget(budgetId: number): Observable<void> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    });
    return this.http.delete<void>(`${this.apiUrl}/${budgetId}`, { headers });
  }
}
