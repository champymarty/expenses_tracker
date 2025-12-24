import { TestBed } from '@angular/core/testing';

import { Source } from './source';

describe('Source', () => {
  let service: Source;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Source);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
