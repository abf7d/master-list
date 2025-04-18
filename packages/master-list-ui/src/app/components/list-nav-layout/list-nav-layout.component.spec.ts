import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListNavLayoutComponent } from './list-nav-layout.component';

describe('ListNavLayoutComponent', () => {
  let component: ListNavLayoutComponent;
  let fixture: ComponentFixture<ListNavLayoutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListNavLayoutComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListNavLayoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
