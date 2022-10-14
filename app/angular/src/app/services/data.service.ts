import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { GraphData } from '../GraphData';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  private apiUrl: string = 'http://127.0.0.1:5000/';

  constructor(private http: HttpClient) { }

  getData(columns: any, endpoint: string): Observable<GraphData> {
    return this.http.post<GraphData>(this.apiUrl + endpoint, columns);
  };
}
