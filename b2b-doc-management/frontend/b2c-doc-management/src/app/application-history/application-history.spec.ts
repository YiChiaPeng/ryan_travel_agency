import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApplicationHistory } from './application-history';

describe('ApplicationHistory', () => {
  let component: ApplicationHistory;
  let fixture: ComponentFixture<ApplicationHistory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApplicationHistory]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApplicationHistory);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
