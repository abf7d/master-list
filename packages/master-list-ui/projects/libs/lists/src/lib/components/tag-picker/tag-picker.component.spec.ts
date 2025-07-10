import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TagPickerComponent } from './tag-picker.component';

describe('TagPickerComponent', () => {
  let component: TagPickerComponent;
  let fixture: ComponentFixture<TagPickerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TagPickerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TagPickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
