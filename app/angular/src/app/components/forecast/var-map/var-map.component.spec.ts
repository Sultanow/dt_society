import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VarMapComponent } from './var-map.component';

describe('VarMapComponent', () => {
  let component: VarMapComponent;
  let fixture: ComponentFixture<VarMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VarMapComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VarMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
