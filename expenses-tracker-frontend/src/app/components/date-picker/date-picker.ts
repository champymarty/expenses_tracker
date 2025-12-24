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
import { DateRangeService, DatePickerData } from '../../services/date-range.service';
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

// DatePickerData is provided by `DateRangeService`

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

  constructor(private dateRangeService: DateRangeService) {}

  @Output() onDatesSelected = new EventEmitter<DatePickerData>();

  ngOnInit() {
    // initialize from the shared service
    const current = this.dateRangeService.value;
    if (current.startDate) this.startDate.setValue(moment(current.startDate));
    else this.startDate.reset();
    if (current.endDate) this.endDate.setValue(moment(current.endDate));
    else this.endDate.reset();

    // keep in sync if another component updates the shared range
    this.dateRangeService.dates$.subscribe(d => {
      if (d.startDate) this.startDate.setValue(moment(d.startDate));
      else this.startDate.reset();
      if (d.endDate) this.endDate.setValue(moment(d.endDate));
      else this.endDate.reset();
      this.markAsDirtyAndUpdate();
    });
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
    const formData: DatePickerData = {
      startDate: this.startDate.value?.toDate() ?? null,
      endDate: this.endDate.value?.toDate() ?? null,
    };
    // update shared state and notify parent
    this.dateRangeService.setDates(formData);
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

  isPreviousMonth() {
    const start = moment().subtract(1, 'months').startOf('month');
    const end = moment().subtract(1, 'months').endOf('month');
    return (
      (this.startDate.value?.isSame(start, 'month') ?? false) &&
      (this.endDate.value?.isSame(end, 'month') ?? false)
    );
  }

  onLastXMonth(monthsMinus: number) {
    this.startDate.setValue(moment().subtract(monthsMinus, 'months').startOf('month'));
    this.endDate.setValue(moment().endOf('month'));
    this.markAsDirtyAndUpdate();
    this.onAppyPressed();
  }

  isOnLastXMonth(monthsMinus: number): boolean {
    const start = moment().subtract(monthsMinus, 'months').startOf('month');
    const end = moment().endOf('month');
    return (
      (this.startDate.value?.isSame(start, 'month') ?? false) &&
      (this.endDate.value?.isSame(end, 'month') ?? false)
    );
  }

  thisYear() {
    this.startDate.setValue(moment().startOf('year'));
    this.endDate.setValue(moment().endOf('month'));
    this.markAsDirtyAndUpdate();
    this.onAppyPressed();
  }

  isThisYear() {
    const start = moment().startOf('year');
    const end = moment().endOf('month');
    return (
      (this.startDate.value?.isSame(start, 'month') ?? false) &&
      (this.endDate.value?.isSame(end, 'month') ?? false)
    );
  }

  onClear() {
    this.startDate.reset();
    this.endDate.reset();
    const cleared: DatePickerData = { startDate: null, endDate: null };
    this.dateRangeService.setDates(cleared);
    this.onDatesSelected.emit(cleared);
  }
}
