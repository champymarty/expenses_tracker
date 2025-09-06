import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SourceTab } from './source-tab';

describe('SourceTab', () => {
  let component: SourceTab;
  let fixture: ComponentFixture<SourceTab>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SourceTab]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SourceTab);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
