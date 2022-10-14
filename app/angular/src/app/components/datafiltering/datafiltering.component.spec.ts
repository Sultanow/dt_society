import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatafilteringComponent } from './datafiltering.component';

describe('DatafilteringComponent', () => {
  let component: DatafilteringComponent;
  let fixture: ComponentFixture<DatafilteringComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DatafilteringComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DatafilteringComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
