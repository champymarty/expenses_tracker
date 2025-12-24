import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CategoryBoard } from './category-board';

describe('CategoryBoard', () => {
  let component: CategoryBoard;
  let fixture: ComponentFixture<CategoryBoard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CategoryBoard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CategoryBoard);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
