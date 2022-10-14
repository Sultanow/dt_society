import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProphetscenariosComponent } from './prophetscenarios.component';

describe('ProphetscenariosComponent', () => {
  let component: ProphetscenariosComponent;
  let fixture: ComponentFixture<ProphetscenariosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProphetscenariosComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProphetscenariosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
