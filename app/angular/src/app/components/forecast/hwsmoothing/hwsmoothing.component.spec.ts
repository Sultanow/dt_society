import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HwsmoothingComponent } from './hwsmoothing.component';

describe('HwsmoothingComponent', () => {
  let component: HwsmoothingComponent;
  let fixture: ComponentFixture<HwsmoothingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HwsmoothingComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HwsmoothingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
