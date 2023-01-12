import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VarforecastsComponent } from './varforecasts.component';

describe('VarforecastsComponent', () => {
  let component: VarforecastsComponent;
  let fixture: ComponentFixture<VarforecastsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VarforecastsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VarforecastsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
