import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UploaddialogComponent } from './uploaddialog.component';

describe('UploaddialogComponent', () => {
  let component: UploaddialogComponent;
  let fixture: ComponentFixture<UploaddialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UploaddialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UploaddialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
