import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NavTileComponent } from './nav-tile.component';

describe('NavTileComponent', () => {
  let component: NavTileComponent;
  let fixture: ComponentFixture<NavTileComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavTileComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NavTileComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
