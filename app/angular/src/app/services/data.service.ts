import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DataService {

  private apiUrl: string = 'http://127.0.0.1:5000/';

  constructor(private http: HttpClient) { }

  getData(columns: any, endpoint: string): Observable<Object> {

    return this.http.post<Object>(this.apiUrl + endpoint, columns);
  };
}
