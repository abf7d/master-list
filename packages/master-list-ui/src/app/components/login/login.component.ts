import { Component } from '@angular/core';
import { MsalService } from '@master-list/auth';

@Component({
  selector: 'app-login',
  imports: [],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  constructor(private authService: MsalService) {}
  ngOnInit(): void {
      this.authService.login();
  }
}
