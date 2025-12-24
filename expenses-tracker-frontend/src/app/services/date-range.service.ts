import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import * as _moment from 'moment';
import { default as _rollupMoment } from 'moment';

const moment = _rollupMoment || _moment;

export interface DatePickerData {
  startDate: Date | null;
  endDate: Date | null;
}

@Injectable({ providedIn: 'root' })
export class DateRangeService {
  private STORAGE_KEY = 'app_date_range';
  private subject = new BehaviorSubject<DatePickerData>(this.loadFromStorage());

  readonly dates$ = this.subject.asObservable();

  get value(): DatePickerData {
    return this.subject.getValue();
  }

  setDates(dates: DatePickerData) {
    this.subject.next(dates);
    try {
      localStorage.setItem(
        this.STORAGE_KEY,
        JSON.stringify({
          startDate: dates.startDate ? dates.startDate.toISOString() : null,
          endDate: dates.endDate ? dates.endDate.toISOString() : null,
        }),
      );
    } catch (e) {
      // ignore storage errors
    }
  }

  private loadFromStorage(): DatePickerData {
    try {
      const raw = localStorage.getItem(this.STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        return {
          startDate: parsed.startDate ? new Date(parsed.startDate) : null,
          endDate: parsed.endDate ? new Date(parsed.endDate) : null,
        };
      }
    } catch (_) {}

    return {
      startDate: moment().startOf('month').toDate(),
      endDate: moment().endOf('month').toDate(),
    };
  }
}
