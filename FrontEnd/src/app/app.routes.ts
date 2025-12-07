import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Register } from './register/register';
import { Dashboard } from './dashboard/dashboard';
import { Predictions } from './predictions/predictions';
import { Matches } from './matches/matches';
import { Team } from './team/team';

export const routes: Routes = [
    { path: '', redirectTo: 'login', pathMatch: 'full' },
    { path: 'login', component: Login },
    { path: 'register', component: Register },
    { path: 'dashboard', component: Dashboard },
    { path: 'matches', component: Matches },
    { path: 'predictions', component: Predictions },
    { path: 'teams', component: Team },
];
