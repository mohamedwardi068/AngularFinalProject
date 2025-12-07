import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';
import { CommonModule, DatePipe } from '@angular/common';
import { Router } from '@angular/router';

@Component({
    selector: 'app-matches',
    standalone: true,
    imports: [CommonModule, DatePipe],
    templateUrl: './matches.html',
    styleUrl: './matches.css'
})
export class Matches implements OnInit {
    api = inject(ApiService);
    router = inject(Router);
    matches: any[] = [];
    competition = 'PL';

    competitions = [
        { code: 'PL', name: 'Premier League' },
        { code: 'BL1', name: 'Bundesliga' },
        { code: 'SA', name: 'Serie A' },
        { code: 'PD', name: 'La Liga' },
        { code: 'FL1', name: 'Ligue 1' },
        { code: 'CL', name: 'Champions League' }
    ];

    ngOnInit() {
        this.loadMatches();
    }

    onCompChange(code: string) {
        this.competition = code;
        this.loadMatches();
    }

    loadMatches() {
        this.api.getMatches(this.competition).subscribe({
            next: (res) => {
                this.matches = res || [];
            },
            error: (err) => console.error(err)
        });
    }

    predict(match: any) {
        // Navigate to predictions page with match details
        this.router.navigate(['/predictions'], {
            queryParams: {
                competition: this.competition,
                fixtureId: match.id,
                home: match.homeTeam.name,
                away: match.awayTeam.name,
                utcDate: match.utcDate
            }
        });
    }
}
