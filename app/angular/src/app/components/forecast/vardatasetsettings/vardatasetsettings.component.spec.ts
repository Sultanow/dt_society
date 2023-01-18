import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VardatasetsettingsComponent } from './vardatasetsettings.component';

describe('VardatasetsettingsComponent', () => {
  let component: VardatasetsettingsComponent;
  let fixture: ComponentFixture<VardatasetsettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VardatasetsettingsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VardatasetsettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
