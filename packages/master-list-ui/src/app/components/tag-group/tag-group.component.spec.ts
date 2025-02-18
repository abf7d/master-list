import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TagGroupComponent } from './tag-group.component';

describe('TagGroupComponent', () => {
  let component: TagGroupComponent;
  let fixture: ComponentFixture<TagGroupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TagGroupComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TagGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
