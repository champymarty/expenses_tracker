import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs/internal/observable/of';
import { Observable } from 'rxjs/internal/Observable';
import { CategoryFamily } from '../objects/category-family';
import { CombineCategoryFamily } from '../objects/combine-category-family';

@Injectable({
  providedIn: 'root',
})
export class CategoryFamilyService {
  private readonly apiUrl = environment.apiBaseUrl + '/category-family';
  private cache: CategoryFamily[] | null = null;

  constructor(private http: HttpClient) {}

  getAllCategoryFamilies(): Observable<CategoryFamily[]> {
    if (this.cache) {
      return of(this.cache);
    }
    const headers = new HttpHeaders({ Accept: 'application/json' });
    return new Observable<CategoryFamily[]>(subscriber => {
      this.http.get<CategoryFamily[]>(this.apiUrl, { headers }).subscribe({
        next: data => {
          this.cache = data;
          subscriber.next(data);
          subscriber.complete();
        },
        error: err => subscriber.error(err),
      });
    });
  }

  updateCategoryFamilyRegex(
    categoryFamilyId: number,
    regexPattern: string | null,
  ): Observable<CategoryFamily> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    });
    const body = { regex_pattern: regexPattern };
    this.cache = null; // Invalidate cache
    return this.http.patch<CategoryFamily>(`${this.apiUrl}/${categoryFamilyId}/regex`, body, {
      headers,
    });
  }

  recalculateExpenseCategoryFamily(): Observable<{ updated_expenses: number }> {
    const headers = new HttpHeaders({ Accept: 'application/json' });
    this.cache = null; // Invalidate cache
    return this.http.post<{ updated_expenses: number }>(
      `${this.apiUrl}/recalculate-expense-category-family`,
      {},
      { headers },
    );
  }

  getAllCategoryFamiliesWithMappings(): Observable<CategoryFamily[]> {
    const headers = new HttpHeaders({ Accept: 'application/json' });
    return this.http.get<CategoryFamily[]>(`${this.apiUrl}/mapping`, { headers });
  }

  combineCategoryFamily(combineCategoryFamily: CombineCategoryFamily): Observable<CategoryFamily> {
    const headers = new HttpHeaders({ Accept: 'application/json' });
    this.cache = null; // Invalidate cache
    return this.http.patch<CategoryFamily>(`${this.apiUrl}/combine`, combineCategoryFamily, {
      headers,
    });
  }
}
