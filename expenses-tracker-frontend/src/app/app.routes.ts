import { Routes } from '@angular/router';
import { App } from './app';
import { Dashboard } from './components/dashboard/dashboard';
import { Expenses } from './components/expenses/expenses';
import { Data } from './components/data/data';
import { CategoryBoard } from './components/category-board/category-board';
import { SourceTab } from './components/source-tab/source-tab';

export const routes: Routes = [
  { path: 'dashboard', component: Dashboard },
  { path: 'expenses', component: Expenses },
  { path: 'categories', component: CategoryBoard },
  { path: 'sources', component: SourceTab },
  { path: 'data', component: Data },
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' }, // default route
  { path: '**', redirectTo: '/dashboard' }, // wildcard route
];
