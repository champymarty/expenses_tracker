import { Component, Inject } from '@angular/core';
import { AsyncPipe, CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepicker, MatDatepickerModule } from '@angular/material/datepicker';
import {
  DateAdapter,
  MAT_DATE_FORMATS,
  MAT_DATE_LOCALE,
  MatNativeDateModule,
  provideNativeDateAdapter,
} from '@angular/material/core';
import { ExpensesService } from '../../../services/expenses-service';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { Moment } from 'moment';
import moment from 'moment';
import { MomentDateAdapter } from '@angular/material-moment-adapter';
import { MY_FORMATS } from '../../date-picker/date-picker';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { map, Observable, startWith } from 'rxjs';
import { CategoryFamilyService } from '../../../services/category-family';
import { SourceService } from '../../../services/source-service';
import { Source } from '../../../objects/source';
import { MatSelectModule } from '@angular/material/select';
import { Expense } from '../../../objects/expense';
import { CreateExpensePayload } from '../../../objects/create-expense-payload';

@Component({
  selector: 'app-create-expense-component',
  standalone: true,
  providers: [
    provideNativeDateAdapter(),
    { provide: DateAdapter, useClass: MomentDateAdapter, deps: [MAT_DATE_LOCALE] },
    { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
  ],
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    FormsModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatDatepickerModule,
    MatDialogModule,
    MatNativeDateModule,
    MatAutocompleteModule,
    AsyncPipe,
  ],
  templateUrl: './create-expense-component.html',
  styleUrl: './create-expense-component.scss',
})
export class CreateExpenseComponent {
  expenseForm: FormGroup;
  creationDate = new FormControl<Moment>(moment(), Validators.required);
  originalCategory = new FormControl<string>('', Validators.required);
  source = new FormControl<Source | null>(null, Validators.required);

  categoryFamilies: string[] = [];
  filteredCategoryFamilies: Observable<string[]>;

  availableSources: Source[] = [];

  errorMessage: string = '';

  constructor(
    public dialogRef: MatDialogRef<CreateExpenseComponent>,
    private fb: FormBuilder,
    private categoryFamilyService: CategoryFamilyService,
    private expensesService: ExpensesService,
    private sourceService: SourceService,
    @Inject(MAT_DIALOG_DATA) public data: any,
  ) {
    this.expenseForm = this.fb.group({
      creationDate: this.creationDate,
      description: ['', Validators.required],
      amount: ['', [Validators.required, Validators.min(0)]],
      originalCategory: this.originalCategory,
      source: this.source,
    });
    this.filteredCategoryFamilies = this.originalCategory.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value || '')),
    );
  }

  ngOnInit(): void {
    this.categoryFamilyService.getAllCategoryFamilies().subscribe(data => {
      this.categoryFamilies = data.map(cf => cf.name);
      this.categoryFamilies.sort((a, b) => a.localeCompare(b));
    });
    this.filteredCategoryFamilies = this.originalCategory.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value || '')),
    );
    this.sourceService.getAllSources().subscribe(data => {
      this.availableSources = data;
    });
  }

  chosenYearHandler(formControl: FormControl<Moment | null>, normalizedYear: Moment) {
    const ctrlValue = formControl.value;
    if (!ctrlValue) return;
    ctrlValue.year(normalizedYear.year());
    formControl.setValue(ctrlValue.startOf('month'));
  }

  chosenMonthHandler(
    formControl: FormControl<Moment | null>,
    normalizedMonth: Moment,
    datepicker: MatDatepicker<Moment>,
  ) {
    const ctrlValue = formControl.value;
    if (!ctrlValue) return;
    ctrlValue.month(normalizedMonth.month());
    formControl.setValue(ctrlValue.startOf('month'));
    datepicker.close();
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();
    if (filterValue === '') {
      return this.categoryFamilies;
    }
    return this.categoryFamilies.filter(categoryFamilyName =>
      categoryFamilyName.toLowerCase().includes(filterValue),
    );
  }

  onSubmit() {
    if (this.expenseForm.valid) {
      const expenseData = this.expenseForm.value;
      const expenseDto = {
        description: expenseData.description,
        amount: expenseData.amount,
        date: expenseData.creationDate.format('YYYY-MM-DD'),
        category_name: expenseData.originalCategory,
        sourceId: expenseData.source.id,
      } as unknown as CreateExpensePayload;
      this.expensesService.createExpense(expenseDto).subscribe({
        next: response => {
          this.errorMessage = '';
          this.dialogRef.close(response);
        },
        error: err => {
          this.errorMessage = `Error code ${err.status}. ${err.error?.detail}`;
        },
      });
    }
  }

  onCancel() {
    this.dialogRef.close();
  }
}
