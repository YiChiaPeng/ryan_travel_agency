import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { YourComponent } from './components/your-component/your-component.component'; // Replace with actual component paths
import { YourService } from './services/your-service.service'; // Replace with actual service paths

@NgModule({
  declarations: [
    AppComponent,
    YourComponent // Add your components here
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule
  ],
  providers: [YourService], // Add your services here
  bootstrap: [AppComponent]
})
export class AppModule { }