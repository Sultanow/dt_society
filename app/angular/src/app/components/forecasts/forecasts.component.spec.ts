import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ForecastsComponent } from './forecasts.component';

describe('ForecastsComponent', () => {
  let component: ForecastsComponent;
  let fixture: ComponentFixture<ForecastsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ForecastsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ForecastsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
