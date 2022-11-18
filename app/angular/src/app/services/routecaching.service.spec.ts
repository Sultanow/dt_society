import { TestBed } from '@angular/core/testing';

import { RoutecachingService } from './routecaching.service';

describe('RoutecachingService', () => {
  let service: RoutecachingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RoutecachingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
