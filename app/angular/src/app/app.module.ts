import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HistoryComponent } from './components/graph/history/history.component';

import * as PlotlyJS from 'plotly.js-dist-min';
import { PlotlyModule } from 'angular-plotly.js';
import { MapComponent } from './components/graph/map/map.component';
import { HeatmapComponent } from './components/graph/heatmap/heatmap.component';
import { CorrelationComponent } from './components/graph/correlation/correlation.component';
import { VectorautoregressionComponent } from './components/forecast/vectorautoregression/vectorautoregression.component';
import { ProphetscenariosComponent } from './components/forecast/prophetscenarios/prophetscenarios.component';
import { FileuploadComponent } from './components/fileupload/fileupload.component';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatRadioModule } from '@angular/material/radio';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DatafilteringComponent } from './components/datafiltering/datafiltering.component';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDialogModule } from '@angular/material/dialog';
import { UploaddialogComponent } from './components/datafiltering/uploaddialog/uploaddialog.component';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSliderModule } from '@angular/material/slider';
import { DatatableComponent } from './components/graph/datatable/datatable.component';
import { MatTableModule } from '@angular/material/table';
import { StatisticsComponent } from './components/graph/statistics/statistics.component';
import { NgxSliderModule } from '@angular-slider/ngx-slider';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { MatSidenavModule } from '@angular/material/sidenav';
import { OverviewComponent } from './components/overview/overview.component';
import { ForecastsComponent } from './components/forecasts/forecasts.component';
import { CorrelationsComponent } from './components/correlations/correlations.component';
import { RouterModule } from '@angular/router';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
  declarations: [
    AppComponent,
    HistoryComponent,
    MapComponent,
    HeatmapComponent,
    CorrelationComponent,
    VectorautoregressionComponent,
    ProphetscenariosComponent,
    FileuploadComponent,
    DatafilteringComponent,
    UploaddialogComponent,
    DatatableComponent,
    StatisticsComponent,
    OverviewComponent,
    ForecastsComponent,
    CorrelationsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    PlotlyModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatIconModule,
    MatExpansionModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatSlideToggleModule,
    MatRadioModule,
    FormsModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatTabsModule,
    ReactiveFormsModule,
    MatToolbarModule,
    MatButtonToggleModule,
    MatDialogModule,
    MatSnackBarModule,
    MatSliderModule,
    MatTableModule,
    NgxSliderModule,
    MatCardModule,
    MatDividerModule,
    FontAwesomeModule,
    MatSidenavModule,
    MatDividerModule,
    BrowserModule,
    RouterModule.forRoot([
      {path: 'overview', component: OverviewComponent},
      {path: 'correlations', component: CorrelationsComponent},
      {path: 'forecasts', component: ForecastsComponent},
    ])
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
