import { TestBed } from '@angular/core/testing';

import { CategoryFamily } from './category-family';

describe('CategoryFamily', () => {
  let service: CategoryFamily;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CategoryFamily);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
