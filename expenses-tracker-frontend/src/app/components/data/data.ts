import { Component } from '@angular/core';
import { SourceService } from '../../services/source-service';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { FormControl, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Source } from '../../objects/source';
import { ExpensesService } from '../../services/expenses-service';
import { MatDialog } from '@angular/material/dialog';
import { InfoDialogComponent } from '../info-dialog-component/info-dialog-component';
import { ErrorDialog } from '../error-dialog/error-dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-data',
  imports: [
    MatFormFieldModule,
    MatSelectModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './data.html',
  styleUrl: './data.scss',
})
export class Data {
  sources: Source[] = [];
  selectedFiles: File[] = [];
  sourceControl = new FormControl<Source | null>(null, Validators.required);

  constructor(
    private sourceService: SourceService,
    private expensesService: ExpensesService,
    public dialog: MatDialog,
  ) {}

  ngOnInit() {
    this.sourceService.getAllSources().subscribe(sources => {
      this.sources = sources;
      this.sources.unshift({ id: -1, name: 'Auto', type: 'auto' });
      this.sourceControl.setValue(this.sources[0]);
    });
  }

  onFileSelected(event: any) {
    const files: FileList = event.target.files;
    this.selectedFiles = Array.from(files);
  }

  isDisabled() {
    return !this.sourceControl.errors && this.selectedFiles.length === 0;
  }

  uploadExpenses() {
    if (this.sourceControl.value && this.selectedFiles.length > 0) {
      let source_id: number | null = this.sourceControl.value.id;
      if (this.sourceControl.value.type === 'auto') {
        source_id = null;
      }
      this.expensesService.upload_expenses(this.selectedFiles, source_id).subscribe({
        next: expensesUpload => {
          this.dialog.open(InfoDialogComponent, {
            width: '400px',
            data: {
              title: 'Upload successfull',
              message: `New expenses ${expensesUpload.created_expenses}. Existing expenses ${expensesUpload.existing_expenses}`,
              listMessageTitle: 'Failed to extract files: ',
              messages: expensesUpload.filesFailedToExtract?.map(
                fileError => `${fileError.filename}: ${fileError.reason}`,
              ),
            },
          });
        },
        error: err => {
          this.dialog.open(ErrorDialog, {
            data: {
              code: err.status,
              message: err?.error?.detail || 'Failed to upload expenses. No error messages',
            },
          });
        },
      });
    }
  }

  exportDb() {
    this.expensesService.exportDatabase().subscribe(blob => {
      // Handle the downloaded file
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'expenses_tracker.sql';
      link.click();
    });
  }
}
