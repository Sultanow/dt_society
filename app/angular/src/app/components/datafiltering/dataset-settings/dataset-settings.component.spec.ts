import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DatasetSettingsComponent } from './dataset-settings.component';

describe('DatasetSettingsComponent', () => {
  let component: DatasetSettingsComponent;
  let fixture: ComponentFixture<DatasetSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DatasetSettingsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DatasetSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
