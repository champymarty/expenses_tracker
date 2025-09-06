import { Component, EventEmitter, Output } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { provideNativeDateAdapter } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatDividerModule } from '@angular/material/divider';
import { MomentDateAdapter } from '@angular/material-moment-adapter';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatDatepicker } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
// Depending on whether rollup is used, moment needs to be imported differently.
// Since Moment.js doesn't have a default export, we normally need to import using the `* as`
// syntax. However, rollup creates a synthetic default module and we thus need to import it using
// the `default as` syntax.
import * as _moment from 'moment';
// tslint:disable-next-line:no-duplicate-imports
import { default as _rollupMoment, Moment } from 'moment';

const moment = _rollupMoment || _moment;

// See the Moment.js docs for the meaning of these formats:
// https://momentjs.com/docs/#/displaying/format/
export const MY_FORMATS = {
  parse: {
    dateInput: 'MM/YYYY',
  },
  display: {
    dateInput: 'MM/YYYY',
    monthYearLabel: 'MMM YYYY',
    dateA11yLabel: 'LL',
    monthYearA11yLabel: 'MMMM YYYY',
  },
};

export interface DatePickerData {
  startDate: Date | null | undefined;
  endDate: Date | null | undefined;
}

@Component({
  selector: 'app-date-picker',
  providers: [
    provideNativeDateAdapter(),
    { provide: DateAdapter, useClass: MomentDateAdapter, deps: [MAT_DATE_LOCALE] },
    { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
  ],
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatDividerModule,
    MatIconModule,
  ],
  templateUrl: './date-picker.html',
  styleUrl: './date-picker.scss',
})
export class DatePicker {
  startDate = new FormControl<Moment>(moment());
  endDate = new FormControl<Moment>(moment());

  @Output() onDatesSelected = new EventEmitter<DatePickerData>();

  ngOnInit() {
    this.onLastXMonth(0);
  }

  setDateFormValue(value: Moment, formControl: FormControl) {
    if (formControl === this.startDate) {
      formControl.setValue(value.startOf('month'));
    } else {
      formControl.setValue(value.endOf('month'));
    }
  }

  chosenYearHandler(formControl: FormControl, normalizedYear: Moment) {
    const ctrlValue = formControl.value;
    if (!ctrlValue) return;
    ctrlValue.year(normalizedYear.year());
    this.setDateFormValue(ctrlValue, formControl);
  }

  chosenMonthHandler(
    formControl: FormControl,
    normalizedMonth: Moment,
    datepicker: MatDatepicker<Moment>,
  ) {
    const ctrlValue = formControl.value;
    if (!ctrlValue) return;
    ctrlValue.month(normalizedMonth.month());
    this.setDateFormValue(ctrlValue, formControl);
    datepicker.close();
  }

  onAppyPressed() {
    const formData = {
      startDate: this.startDate.value?.toDate(),
      endDate: this.endDate.value?.toDate(),
    };
    this.onDatesSelected.emit(formData);
  }

  markAsDirtyAndUpdate() {
    this.startDate.markAsDirty();
    this.endDate.markAsDirty();
    this.startDate.updateValueAndValidity();
    this.endDate.updateValueAndValidity();
  }

  onPreviousMonth() {
    this.startDate.setValue(moment().subtract(1, 'months').startOf('month'));
    this.endDate.setValue(moment().subtract(1, 'months').endOf('month'));
    this.markAsDirtyAndUpdate();
    this.onAppyPressed();
  }

  onLastXMonth(monthsMinus: number) {
    this.startDate.setValue(moment().subtract(monthsMinus, 'months').startOf('month'));
    this.endDate.setValue(moment().endOf('month'));
    this.markAsDirtyAndUpdate();
    this.onAppyPressed();
  }

  thisYear() {
    this.startDate.setValue(moment().startOf('year'));
    this.endDate.setValue(moment().endOf('month'));
    this.markAsDirtyAndUpdate();
    this.onAppyPressed();
  }

  onClear() {
    this.startDate.reset();
    this.endDate.reset();
    this.onAppyPressed();
  }
}
