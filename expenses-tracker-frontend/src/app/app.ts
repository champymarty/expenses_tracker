import { Component } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MatTabsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  protected title = 'expense-tracker';
  links = ['dashboard', 'expenses', 'categories', 'sources', 'data'];
  activeLink = this.links[0];

  constructor(private router: Router) {
    // Set activeLink based on current route on load and navigation
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        const url = event.urlAfterRedirects.split('/')[1];
        if (this.links.includes(url)) {
          this.activeLink = url;
        }
      }
    });
  }

  selectTab(link: string): void {
    this.activeLink = link;
    this.router.navigate([`/${link}`]); // <-- navigate to route
  }
}
