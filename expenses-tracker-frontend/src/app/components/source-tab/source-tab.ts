import { Component } from '@angular/core';
import { DatePicker } from '../date-picker/date-picker';
import { Source } from '../../objects/source';
import { SourceAverage } from '../../objects/source-average';
import { SourceService } from '../../services/source-service';
import { MatTableModule } from '@angular/material/table';
import { DecimalPipe } from '@angular/common';
import { DatePickerData, DateRangeService } from '../../services/date-range.service';

@Component({
  selector: 'app-source-tab',
  imports: [DatePicker, MatTableModule, DecimalPipe],
  templateUrl: './source-tab.html',
  styleUrl: './source-tab.scss',
})
export class SourceTab {
  startDate: string | null = null;
  endDate: string | null = null;

  averages: SourceAverage[] = [];

  totalAverage: number = 0;
  averageSource: number = 0;

  constructor(
    private sourceService: SourceService,
    private dataRangeService: DateRangeService,
  ) {}

  ngOnInit() {
    this.dataRangeService.dates$.subscribe((datePickerData: DatePickerData) => {
      this.processOnDatesSelected(datePickerData);
    });
  }

  fetchAverages() {
    this.sourceService.getAllSourceAverages(this.startDate, this.endDate).subscribe({
      next: data => {
        this.averages = data;
        console.log('Source averages fetched successfully:', this.averages);
        this.processAverages();
      },
      error: err => {
        console.error('Error fetching source averages:', err);
      },
    });
  }

  processAverages() {
    if (this.averages.length === 0) {
      this.totalAverage = 0;
      return;
    }
    const total = this.averages.reduce((sum, entry) => sum + entry.average, 0);
    this.totalAverage = total;
    this.averageSource = total / this.averages.length;
  }

  convertDateToString(date: Date | null | undefined): string | null {
    if (!date) return null;
    return date.toISOString().split('T')[0];
  }

  processOnDatesSelected(datePickerData: DatePickerData) {
    console.log('Selected Dates:', datePickerData);
    this.startDate = this.convertDateToString(datePickerData.startDate);
    this.endDate = this.convertDateToString(datePickerData.endDate);
    this.fetchAverages();
  }
}
