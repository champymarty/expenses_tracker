import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { CategoryFamily } from '../../objects/category-family';
import { CategoryService } from '../../services/category-service';
import { CategoryFamilyService } from '../../services/category-family';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { CombineCategoryFamily } from '../../objects/combine-category-family';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

export interface CombineCategoryFamilyDialogInput {
  categoryFamilies: CategoryFamily[];
}

export interface CombineCategoryFamilyDialogOutput {
  newCategoryFamily: CategoryFamily;
  deletedCategoryFamilyId: number;
}

@Component({
  selector: 'app-combine-category-family-dialog',
  imports: [
    MatFormFieldModule,
    MatSelectModule,
    FormsModule,
    ReactiveFormsModule,
    MatInputModule,
    MatDialogModule,
    MatButtonModule,
  ],
  templateUrl: './combine-category-family-dialog.html',
  styleUrl: './combine-category-family-dialog.scss',
})
export class CombineCategoryFamilyDialog {
  survivingCategoryFamilyControl = new FormControl<CategoryFamily | null>(
    null,
    Validators.required,
  );
  deletedCategoryFamily = new FormControl<CategoryFamily | null>(null, Validators.required);
  nameFormControl = new FormControl('', [Validators.required]);

  combineForm: FormGroup;

  categoryFamilies: CategoryFamily[];

  errorResponseCombine: string | null = null;

  constructor(
    public dialogRef: MatDialogRef<CombineCategoryFamilyDialog>,
    private fb: FormBuilder,
    private categoryFamilyService: CategoryFamilyService,
    @Inject(MAT_DIALOG_DATA) public data: CombineCategoryFamilyDialogInput,
  ) {
    this.categoryFamilies = data.categoryFamilies;
    this.combineForm = this.fb.group({
      survivingCategoryFamilyControl: this.survivingCategoryFamilyControl,
      deletedCategoryFamilyControl: this.deletedCategoryFamily,
      nameFormControl: this.nameFormControl,
    });
  }

  ngOnInit(): void {
    this.survivingCategoryFamilyControl.valueChanges.subscribe(value => {
      if (value && value.name) {
        this.nameFormControl.setValue(value.name);
      }
    });
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  generateCombineCategoryFamily(): CombineCategoryFamily {
    return {
      surviving_cateogy_family_id: this.survivingCategoryFamilyControl.value?.id,
      deleting_cateogy_family_id: this.deletedCategoryFamily.value?.id,
      name: this.nameFormControl.value,
    } as CombineCategoryFamily;
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onConfirm(): void {
    this.categoryFamilyService
      .combineCategoryFamily(this.generateCombineCategoryFamily())
      .subscribe({
        next: updatedFamily => {
          this.dialogRef.close({
            newCategoryFamily: updatedFamily,
            deletedCategoryFamilyId: this.deletedCategoryFamily.value?.id,
          } as CombineCategoryFamilyDialogOutput);
        },
        error: err => {
          this.errorResponseCombine =
            err?.error?.detail || 'An error occurred while combining category families.';
        },
      });
  }
}
