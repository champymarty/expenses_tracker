import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CategoryFamilyCellEditor } from './category-family-cell-editor';

describe('CategoryFamilyCellEditor', () => {
  let component: CategoryFamilyCellEditor;
  let fixture: ComponentFixture<CategoryFamilyCellEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CategoryFamilyCellEditor]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CategoryFamilyCellEditor);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
