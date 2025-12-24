import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { BudgetService } from '../../services/budget-service';
import { AverageBudget } from '../../objects/average-budget';
import { CategoryFamily } from '../../objects/category-family';
import { CategoryFamilyService } from '../../services/category-family';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  FormGroupDirective,
  FormsModule,
  NgForm,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { ErrorStateMatcher } from '@angular/material/core';
import { MatInputModule } from '@angular/material/input';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { Budget } from '../../objects/budget';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { ErrorDialog } from '../error-dialog/error-dialog';
import { DatePicker } from '../date-picker/date-picker';
import { DatePickerData, DateRangeService } from '../../services/date-range.service';

export class MyErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    const isSubmitted = form && form.submitted;
    return !!(control && control.invalid && (control.dirty || control.touched || isSubmitted));
  }
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    DatePicker,
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    MatToolbarModule,
    MatIconModule,
    MatSnackBarModule,
    DatePicker,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  averageBudgets: AverageBudget[] = [];
  categoryFamilies: CategoryFamily[] = [];
  frequencyTypes = [
    { value: 0, viewValue: 'Monthly' },
    { value: 1, viewValue: 'Yearly' },
  ];

  categoryFamilyControl = new FormControl<CategoryFamily | null>(null, Validators.required);
  amountControl = new FormControl(null, [Validators.required, Validators.min(0.01)]);
  frequenceControl = new FormControl<number | null>(null, Validators.required);
  addBudgetForm: FormGroup;

  matcher = new MyErrorStateMatcher();

  startDate: string | null = null;
  endDate: string | null = null;

  constructor(
    private fb: FormBuilder,
    private budgetService: BudgetService,
    private categoryFamilyService: CategoryFamilyService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private dataRangeService: DateRangeService,
  ) {
    this.addBudgetForm = this.fb.group({
      categoryFamilyControl: this.categoryFamilyControl,
      amountControl: this.amountControl,
      frequenceControl: this.frequenceControl,
    });
  }

  roundToNoDecimal(value: number) {
    return value.toFixed(0);
  }

  ngOnInit(): void {
    this.categoryFamilyService.getAllCategoryFamilies().subscribe(data => {
      this.categoryFamilies = data || [];
      this.categoryFamilies.sort((a, b) => a.name.localeCompare(b.name));
    });
    this.dataRangeService.dates$.subscribe((datePickerData: DatePickerData) => {
      this.processOnDatesSelected(datePickerData);
    });
  }

  loadAverageBudgetsData(start: string | null, end: string | null): void {
    this.budgetService.getBudgetCalculations(start, end).subscribe(data => {
      this.averageBudgets = data.averages || [];
    });
  }

  getAverageBudgetTitle(averageBudget: AverageBudget): string {
    let frequency = '';
    if (averageBudget.budget.frequency_type === 0) {
      frequency = 'Monthly';
    } else if (averageBudget.budget.frequency_type === 1) {
      frequency = 'Yearly';
    }
    return `${averageBudget.budget.category_family.name} (${frequency})`;
  }

  onAddBudget() {
    if (this.addBudgetForm.invalid) return;

    const formValue = this.addBudgetForm.value;
    const newBudget: Budget = {
      id: null,
      frequency_type: formValue.frequenceControl.value,
      target_amount: formValue.amountControl,
      category_family: formValue.categoryFamilyControl,
    };

    this.budgetService.createBudget(newBudget).subscribe({
      next: budget => {
        this.loadAverageBudgetsData(this.startDate, this.endDate);
        this.snackBar.open(
          `New Budget with name ${budget.category_family.name} was created !`,
          'Close',
          {
            duration: 4000,
          },
        );
      },
      error: err => {
        console.error('Error creating budget:', err);
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to create budget. No error messages',
          },
        });
      },
    });
  }

  onDeleteBudget(budgetId: number | null) {
    if (budgetId == null) {
      this.dialog.open(ErrorDialog, {
        data: {
          code: 400,
          message: 'Budget ID is required to delete a budget.',
        },
      });
      return;
    }
    this.budgetService.deleteBudget(budgetId).subscribe({
      next: () => {
        this.snackBar.open(`Budget with id ${budgetId} was deleted !`, 'Close', {
          duration: 4000,
        });
        this.averageBudgets = this.averageBudgets.filter(
          avgBudget => avgBudget.budget.id !== budgetId,
        );
      },
      error: err => {
        console.error('Error creating budget:', err);
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to delete budget. No error messages',
          },
        });
      },
    });
  }

  convertDateToString(date: Date | null | undefined): string | null {
    if (!date) return null;
    return date.toISOString().split('T')[0];
  }

  processOnDatesSelected(datePickerData: DatePickerData) {
    console.log('Selected Dates:', datePickerData);
    this.startDate = this.convertDateToString(datePickerData.startDate);
    this.endDate = this.convertDateToString(datePickerData.endDate);
    this.loadAverageBudgetsData(this.startDate, this.endDate);
  }
}
