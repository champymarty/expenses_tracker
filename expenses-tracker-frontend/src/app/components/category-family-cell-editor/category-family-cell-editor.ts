import { Component } from '@angular/core';
import { ICellEditorAngularComp } from 'ag-grid-angular';
import { ICellEditorParams } from 'ag-grid-community';
import { CategoryFamilyService } from '../../services/category-family';
import { CategoryFamily } from '../../objects/category-family';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { AsyncPipe } from '@angular/common';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatInputModule } from '@angular/material/input';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-category-family-cell-editor',
  standalone: true,
  imports: [
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatAutocompleteModule,
    ReactiveFormsModule,
    AsyncPipe,
  ],
  templateUrl: './category-family-cell-editor.html',
  styleUrl: './category-family-cell-editor.scss',
})
export class CategoryFamilyCellEditor implements ICellEditorAngularComp {
  myControl = new FormControl();

  categoryFamilies: CategoryFamily[] = [];
  filteredCategoryFamilies: Observable<CategoryFamily[]>;

  params: ICellEditorParams | undefined;

  selectedCategoryFamily: CategoryFamily | null = null;

  constructor(private categoryFamilyService: CategoryFamilyService) {
    this.filteredCategoryFamilies = this.myControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value || '')),
    );
  }

  agInit(params: ICellEditorParams): void {
    this.params = params;
    this.selectedCategoryFamily = params.value;
    this.categoryFamilyService.getAllCategoryFamilies().subscribe(data => {
      this.categoryFamilies = data;
      this.categoryFamilies.sort((a, b) => a.name.localeCompare(b.name));
    });
    this.filteredCategoryFamilies = this.myControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value || '')),
    );
  }

  getValue(): any {
    return this.selectedCategoryFamily;
  }

  isPopup(): boolean {
    return false;
  }

  private _filter(value: string | CategoryFamily): CategoryFamily[] {
    if (typeof value === 'object' && value !== null) {
      this.selectedCategoryFamily = this.categoryFamilies.filter(
        categoryFamily => categoryFamily.id === value.id,
      )[0];
      this.myControl.setValue(this.selectedCategoryFamily.name, { emitEvent: false });
      return this.categoryFamilies;
    }

    const filterValue = value.toLowerCase();
    if (filterValue === '') {
      return this.categoryFamilies;
    }
    return this.categoryFamilies.filter(categoryFamily =>
      categoryFamily.name.toLowerCase().includes(filterValue),
    );
  }
}
