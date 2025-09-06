import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CategoryFamilyService } from '../../services/category-family';
import { CategoryFamily } from '../../objects/category-family';
import { ErrorDialog } from '../error-dialog/error-dialog';
import { MatDialog } from '@angular/material/dialog';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipEditedEvent, MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { Category } from '../../objects/category';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { LiveAnnouncer } from '@angular/cdk/a11y';
import { CategoryService } from '../../services/category-service';
import {
  CombineCategoryFamilyDialog,
  CombineCategoryFamilyDialogInput,
  CombineCategoryFamilyDialogOutput,
} from '../combine-category-family-dialog/combine-category-family-dialog';

@Component({
  selector: 'app-category-board',
  imports: [
    MatCardModule,
    MatFormFieldModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatInputModule,
  ],
  templateUrl: './category-board.html',
  styleUrl: './category-board.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CategoryBoard {
  readonly addOnBlur = true;
  readonly separatorKeysCodes = [ENTER, COMMA] as const;
  readonly categoryFamilies = signal<CategoryFamily[]>([]);

  constructor(
    private categoryFamilyService: CategoryFamilyService,
    private categoryService: CategoryService,
    private dialog: MatDialog,
  ) {}

  ngOnInit() {
    this.categoryFamilyService.getAllCategoryFamilies().subscribe({
      next: data => {
        this.categoryFamilies.update(families => [...families, ...data]);
        console.log('Category families fetched successfully:', this.categoryFamilies);
      },
      error: err => {
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to getch categories. No error messages',
          },
        });
      },
    });
  }

  addCategoryOnInput(newCategory: Category, categoryFamily: CategoryFamily): void {
    this.categoryFamilies.update(categoryFamilies => {
      const familyIndex = categoryFamilies.findIndex(f => f.id === categoryFamily.id);
      if (familyIndex !== -1) {
        const updatedFamily = { ...categoryFamily };
        updatedFamily.categories = [...(updatedFamily.categories || []), newCategory];
        categoryFamilies[familyIndex] = updatedFamily;
      }
      return [...categoryFamilies];
    });
  }

  add(event: MatChipInputEvent, categoryFamily: CategoryFamily): void {
    const value = (event.value || '').trim();
    if (!value) {
      return;
    }

    const newCategory: Category = {
      id: null,
      name: value,
      category_family_id: categoryFamily.id,
    };

    this.categoryService.addCategory(newCategory).subscribe({
      next: data => {
        this.addCategoryOnInput(data, categoryFamily);
        event.chipInput!.clear();
      },
      error: err => {
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to add category. No error messages',
          },
        });
        event.chipInput!.clear();
      },
    });
  }

  removeCategoryOnInput(category: Category, categoryFamily: CategoryFamily): void {
    this.categoryFamilies.update(categoryFamilies => {
      const familyIndex = categoryFamilies.findIndex(f => f.id === categoryFamily.id);
      if (familyIndex !== -1) {
        const updatedFamily = { ...categoryFamily };
        updatedFamily.categories =
          updatedFamily.categories?.filter(c => c.id !== category.id) || [];
        categoryFamilies[familyIndex] = updatedFamily;
      }
      return [...categoryFamilies];
    });
  }

  remove(category: Category, categoryFamily: CategoryFamily): void {
    this.categoryService.deleteBudget(category.id!).subscribe({
      next: () => {
        this.removeCategoryOnInput(category, categoryFamily);
      },
      error: err => {
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to remove category. No error messages',
          },
        });
      },
    });
  }

  onCombineCategoryFamily() {
    const dialogRef = this.dialog.open(CombineCategoryFamilyDialog, {
      width: '400px',
      data: { categoryFamilies: this.categoryFamilies() } as CombineCategoryFamilyDialogInput,
    });

    dialogRef.afterClosed().subscribe((combineResult: CombineCategoryFamilyDialogOutput | null) => {
      if (combineResult) {
        this.categoryFamilies.update(categoryFamilies => {
          const familyIndexToDelete = categoryFamilies.findIndex(
            f => f.id === combineResult.deletedCategoryFamilyId,
          );
          if (familyIndexToDelete !== -1) {
            categoryFamilies.splice(familyIndexToDelete, 1);
          }

          const familyIndexToUpdate = categoryFamilies.findIndex(
            f => f.id === combineResult.newCategoryFamily.id,
          );
          if (familyIndexToUpdate !== -1) {
            categoryFamilies[familyIndexToUpdate] = combineResult.newCategoryFamily;
          }
          return [...categoryFamilies];
        });
      }
    });
  }

  onRegexPatternChange(event: Event, categoryFamily: CategoryFamily): void {
    const newPattern = (event.target as HTMLInputElement).value;
    this.categoryFamilyService.updateCategoryFamilyRegex(categoryFamily.id, newPattern).subscribe({
      next: updated => {
        this.categoryFamilies.update(families => {
          const idx = families.findIndex(f => f.id === updated.id);
          if (idx !== -1) {
            families[idx] = updated;
          }
          return [...families];
        });
      },
      error: err => {
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to update regex pattern. No error messages',
          },
        });
      },
    });
  }

  recalculateCategoriesForExpenses(): void {
    this.categoryFamilyService.recalculateExpenseCategoryFamily().subscribe({
      next: result => {
        this.dialog.open(ErrorDialog, {
          data: {
            code: 200,
            message: `Successfully updated ${result.updated_expenses} expenses.`,
          },
        });
      },
      error: err => {
        this.dialog.open(ErrorDialog, {
          data: {
            code: err.status,
            message: err?.error?.detail || 'Failed to recalculate categories. No error messages',
          },
        });
      },
    });
  }
}
