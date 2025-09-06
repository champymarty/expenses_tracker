import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs/internal/Observable';
import { Source } from '../objects/source';
import { SourceAverage } from '../objects/source-average';

@Injectable({
  providedIn: 'root',
})
export class SourceService {
  private readonly apiUrl = environment.apiBaseUrl + '/source';

  constructor(private http: HttpClient) {}

  getAllSources(): Observable<Source[]> {
    const headers = new HttpHeaders({ Accept: 'application/json' });
    return this.http.get<Source[]>(`${this.apiUrl}`, { headers });
  }

  getAllSourceAverages(start?: string | null, end?: string | null): Observable<SourceAverage[]> {
    const headers = new HttpHeaders({ Accept: 'application/json' });
    let params = new HttpParams();
    if (start) {
      params = params.set('start_date', start);
    }
    if (end) {
      params = params.set('end_date', end);
    }
    return this.http.get<SourceAverage[]>(`${this.apiUrl}/averages`, { headers, params });
  }
}
