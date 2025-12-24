import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Category } from '../objects/category';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs/internal/Observable';

@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  private readonly apiUrl = environment.apiBaseUrl + '/category';

  constructor(private http: HttpClient) {}

  addCategory(category: Category): Observable<Category> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    });
    return this.http.post<Category>(this.apiUrl, category, { headers });
  }

  deleteBudget(categoryId: number): Observable<void> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    });
    return this.http.delete<void>(`${this.apiUrl}/${categoryId}`, { headers });
  }
}
