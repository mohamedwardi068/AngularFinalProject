import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../services/api.service';
import { AuthService } from '../services/auth.service';
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
  auth = inject(AuthService); // Inject Auth
  teams: any[] = [];
  myTeam: any = null;
  newTeamName = '';

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    const uid = this.auth.getUserId();
    this.api.getTeams().subscribe(res => {
      this.teams = res;
      if (uid) {
        this.myTeam = this.teams.find(t => t.members.some((m: any) => m.id === uid));
      }
    });
  }

  create() {
    this.api.createTeam(this.newTeamName).subscribe({
      next: () => {
        alert('Team created');
        this.refresh();
      },
      error: (err) => alert(err.error.detail || 'Failed to create team')
    });
  }

  join(id: number) {
    this.api.joinTeam(id).subscribe({
      next: (res) => {
        if (res.msg === 'already member') alert('Already a member');
        else alert('Joined team');
        this.refresh();
      },
      error: (err) => alert(err.error.detail || 'Failed to join')
    });
  }
}
