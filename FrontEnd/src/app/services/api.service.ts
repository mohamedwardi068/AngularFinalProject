import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private apiUrl = 'http://localhost:8000';

  private getHeaders() {
    const token = this.auth.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getLeaderboard(): Observable<any> {
    return this.http.get(`${this.apiUrl}/leaderboard`);
  }

  getMyPredictions(): Observable<any> {
    return this.http.get(`${this.apiUrl}/predictions/me`, { headers: this.getHeaders() });
  }

  submitPrediction(payload: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/predictions`, payload, { headers: this.getHeaders() });
  }

  getTeams(): Observable<any> {
    return this.http.get(`${this.apiUrl}/teams`);
  }

  createTeam(name: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/teams/create`, { name }, { headers: this.getHeaders() });
  }

  joinTeam(team_id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/teams/join`, { team_id }, { headers: this.getHeaders() });
  }

  getMatches(comp: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/matches/${comp}`);
  }
}
