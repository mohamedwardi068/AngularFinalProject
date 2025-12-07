import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-predictions',
  standalone: true,
  imports: [FormsModule, DatePipe],
  templateUrl: './predictions.html',
  styleUrl: './predictions.css',
})
export class Predictions implements OnInit {
  api = inject(ApiService);
  auth = inject(AuthService);
  route = inject(ActivatedRoute);
  myPredictions: any[] = [];

  // Form model
  competition = 'PL';
  fixtureId: number | null = null;
  home = '';
  away = '';
  predicted_home = 0;
  predicted_away = 0;
  utcDate = new Date().toISOString().split('T')[0];

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['home']) {
        this.competition = params['competition'] || 'PL';
        this.fixtureId = params['fixtureId'] ? +params['fixtureId'] : null;
        this.home = params['home'];
        this.away = params['away'];
        this.utcDate = params['utcDate'] ? params['utcDate'].split('T')[0] : this.utcDate;
      }
    });
    this.refresh();
  }

  refresh() {
    this.api.getMyPredictions().subscribe({
      next: (res) => this.myPredictions = res,
      error: (err) => console.error(err)
    });
  }

  submit() {
    const payload = {
      competition: this.competition,
      fixture_id: this.fixtureId,
      home: this.home,
      away: this.away,
      predicted_home: this.predicted_home,
      predicted_away: this.predicted_away,
      utcDate: this.utcDate
    };
    this.api.submitPrediction(payload).subscribe({
      next: () => {
        alert('Prediction submitted!');
        this.refresh();
      },
      error: () => alert('Failed to submit')
    });
  }
}
