import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { TagSelection } from '../../types/tag';

@Injectable({
    providedIn: 'root',
})
export class TagStateService {
    loadOriginTag= new BehaviorSubject<TagSelection | null>(null);
    constructor() {}
}
