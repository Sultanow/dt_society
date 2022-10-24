import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VectorautoregressionComponent } from './vectorautoregression.component';

describe('VectorautoregressionComponent', () => {
  let component: VectorautoregressionComponent;
  let fixture: ComponentFixture<VectorautoregressionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VectorautoregressionComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VectorautoregressionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
