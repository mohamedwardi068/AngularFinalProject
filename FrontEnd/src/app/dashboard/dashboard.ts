import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  api = inject(ApiService);
  auth = inject(AuthService);
  leaderboard: any[] = [];

  ngOnInit() {
    this.api.getLeaderboard().subscribe(res => {
      this.leaderboard = res.leaderboard;
    });
  }
}
