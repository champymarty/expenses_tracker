import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CombineCategoryFamilyDialog } from './combine-category-family-dialog';

describe('CombineCategoryFamilyDialog', () => {
  let component: CombineCategoryFamilyDialog;
  let fixture: ComponentFixture<CombineCategoryFamilyDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CombineCategoryFamilyDialog]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CombineCategoryFamilyDialog);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
