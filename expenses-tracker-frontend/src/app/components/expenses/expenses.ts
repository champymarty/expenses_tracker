import { ChangeDetectionStrategy, Component } from '@angular/core';
import { AgGridAngular } from 'ag-grid-angular';
import {
  AllCommunityModule,
  GridApi,
  GridOptions,
  GridReadyEvent,
  ICellRendererParams,
  type ColDef,
} from 'ag-grid-community';
import { ExpensesService } from '../../services/expenses-service';
import { Expense } from '../../objects/expense';
import { provideNativeDateAdapter } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { ReactiveFormsModule } from '@angular/forms';
import { DatePicker, DatePickerData } from '../date-picker/date-picker';
import { CategoryFamily } from '../../objects/category-family';
import { CategoryFamilyService } from '../../services/category-family';
import { CategoryFamilyCellEditor } from '../category-family-cell-editor/category-family-cell-editor';

@Component({
  selector: 'app-expenses',
  standalone: true,
  imports: [
    AgGridAngular,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    ReactiveFormsModule,
    DatePicker,
  ],
  providers: [provideNativeDateAdapter()],
  templateUrl: './expenses.html',
  styleUrl: './expenses.scss',
})
export class Expenses {
  AG_GRID_MODULES = [AllCommunityModule];
  // Row Data: The data to be displayed.
  rowData: Expense[] = [];
  private gridApi!: GridApi;

  startDate: string | null = null;
  endDate: string | null = null;

  categories: CategoryFamily[] = [];
  categoryNames: string[] = [];

  colDefs: ColDef[] = [
    { field: 'description', headerName: 'Description', sortable: true, filter: true },
    {
      field: 'amount',
      type: 'number',
      headerName: 'Amount',
      valueFormatter: params => {
        if (typeof params.value === 'number') {
          return params.value.toFixed(2);
        }
        return params.value;
      },
    },
    { field: 'date', headerName: 'Date' },
    {
      field: 'categoryFamily',
      headerName: 'Category',
      filter: true,
      cellEditor: 'app-category-family-cell-editor',
      cellRenderer: (params: ICellRendererParams) => {
        return params.value ? params.value.name : '';
      },
      editable: true,
    },
    { field: 'original_category', headerName: 'Original Category', filter: true },
    { field: 'source.name', headerName: 'Source', filter: true },
    {
      field: 'lock_category',
      headerName: 'Locked Category',
      filter: true,
      editable: true,
      valueGetter: params => !!params.data.lock_category,
      valueSetter: params => {
        params.data.lock_category = params.newValue ? 1 : 0;
        return true;
      },
      cellDataType: 'boolean',
    },
    {
      field: 'calculation_status',
      headerName: 'Calculation status',
      filter: true,
      editable: true,
      cellEditor: 'agSelectCellEditor',
      cellEditorParams: {
        values: [null, 'SKIP', 'INCLUDE'],
      },
    },
  ];

  gridOptions: GridOptions = {
    defaultColDef: {
      resizable: true,
      sortable: true,
    },
    getRowId: params => params.data.id.toString(),
    pagination: true,
    paginationPageSize: 20,
    multiSortKey: 'ctrl',
    onCellValueChanged: event => {
      // Only update if the value actually changed
      if (event.newValue !== event.oldValue) {
        const updatedExpense: Expense = { ...event.data, [event.colDef.field!]: event.newValue };
        this.expensesService.patchExpense(updatedExpense).subscribe({
          next: resp => {
            this.gridApi.getRowNode(resp.id.toString())?.setData(resp);
          },
          error: err => {
            // Optionally handle error, e.g. revert value or show error dialog
          },
        });
      }
    },
    components: {
      'app-category-family-cell-editor': CategoryFamilyCellEditor,
    },
  };

  constructor(
    private expensesService: ExpensesService,
    private categoryFamilyService: CategoryFamilyService,
  ) {}

  onGridReady(params: GridReadyEvent) {
    this.gridApi = params.api;
  }

  loadExpenses() {
    this.expensesService.getExpenses(this.startDate, this.endDate).subscribe(data => {
      this.rowData = data.expenses || [];
    });
    this.categoryFamilyService.getAllCategoryFamilies().subscribe(data => {
      this.categories = data;
      this.categoryNames = data.map(cat => cat.name);
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
    this.loadExpenses();
  }
}
