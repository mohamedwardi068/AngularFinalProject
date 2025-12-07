import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-team',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './team.html',
  styleUrl: './team.css',
})
export class Team implements OnInit {
  api = inject(ApiService);
  teams: any[] = [];
  newTeamName = '';

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.api.getTeams().subscribe(res => this.teams = res);
  }

  create() {
    this.api.createTeam(this.newTeamName).subscribe({
      next: () => {
        alert('Team created');
        this.refresh();
      },
      error: () => alert('Failed to create team')
    });
  }

  join(id: number) {
    this.api.joinTeam(id).subscribe({
      next: (res) => {
        if (res.msg === 'already member') alert('Already a member');
        else alert('Joined team');
        this.refresh();
      },
      error: () => alert('Failed to join')
    });
  }
}
