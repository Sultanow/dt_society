import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoryZoomComponent } from './history-zoom.component';

describe('HistoryZoomComponent', () => {
  let component: HistoryZoomComponent;
  let fixture: ComponentFixture<HistoryZoomComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HistoryZoomComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryZoomComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
