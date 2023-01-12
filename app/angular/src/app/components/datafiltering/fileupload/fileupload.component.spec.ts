import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileuploadComponent } from './fileupload.component';

describe('FileuploadComponent', () => {
  let component: FileuploadComponent;
  let fixture: ComponentFixture<FileuploadComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FileuploadComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FileuploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
