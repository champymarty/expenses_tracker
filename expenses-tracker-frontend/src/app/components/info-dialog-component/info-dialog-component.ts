import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-info-dialog-component',
  imports: [MatDialogModule],
  templateUrl: './info-dialog-component.html',
  styleUrl: './info-dialog-component.scss',
})
export class InfoDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA)
    public data: { title: string; message: string; listMessageTitle?: string; messages?: string[] },
  ) {}
}
