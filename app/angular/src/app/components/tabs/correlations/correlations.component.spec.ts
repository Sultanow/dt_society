import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CorrelationsComponent } from './correlations.component';

describe('CorrelationsComponent', () => {
  let component: CorrelationsComponent;
  let fixture: ComponentFixture<CorrelationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CorrelationsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CorrelationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
