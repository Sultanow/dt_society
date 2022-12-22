// Libs
import * as PlotlyJS from 'plotly.js-dist-min';

// Modules
import { PlotlyModule } from 'angular-plotly.js';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgxSliderModule } from '@angular-slider/ngx-slider';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { RouteReuseStrategy, RouterModule } from '@angular/router';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { NgxMatSelectSearchModule } from 'ngx-mat-select-search';
import { NgScrollbarModule } from 'ngx-scrollbar';

// Components
import { AppComponent } from './app.component';
import { HistoryComponent } from './components/graph/history/history.component';
import { MapComponent } from './components/graph/map/map.component';
import { HeatmapComponent } from './components/graph/heatmap/heatmap.component';
import { CorrelationComponent } from './components/graph/correlation/correlation.component';
import { VectorautoregressionComponent } from './components/forecast/vectorautoregression/vectorautoregression.component';
import { ProphetscenariosComponent } from './components/forecast/prophetscenarios/prophetscenarios.component';
import { FileuploadComponent } from './components/fileupload/fileupload.component';
import { DatafilteringComponent } from './components/datafiltering/datafiltering.component';
import { UploaddialogComponent } from './components/datafiltering/uploaddialog/uploaddialog.component';
import { DatatableComponent } from './components/graph/datatable/datatable.component';
import { StatisticsComponent } from './components/graph/statistics/statistics.component';
import { OverviewComponent } from './components/overview/overview.component';
import { CorrelationsComponent } from './components/correlations/correlations.component';
import { DatasetSettingsComponent } from './components/datafiltering/dataset-settings/dataset-settings.component';
import { HistoryZoomComponent } from './components/zoom/history-zoom/history-zoom.component';

// Services
import { AuthService } from './services/auth.service';
import { RoutecachingService } from './services/routecaching.service';

// Material Components
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatRadioModule } from '@angular/material/radio';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSliderModule } from '@angular/material/slider';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MapZoomComponent } from './components/zoom/map-zoom/map-zoom.component';
import { VarMapComponent } from './components/forecast/var-map/var-map.component';

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
    CorrelationsComponent,
    DatasetSettingsComponent,
    MapZoomComponent,
    VarMapComponent,
    HistoryZoomComponent,
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
      {
        path: '',
        redirectTo: '/overview',
        pathMatch: 'full',
        data: { reuse: true },
      },
      {
        path: 'overview',
        component: OverviewComponent,
        pathMatch: 'full',
        data: { reuse: true },
      },
      {
        path: 'correlations',
        component: CorrelationsComponent,
        pathMatch: 'full',
        data: { reuse: true },
      },
      {
        path: 'forecasts/var',
        component: VectorautoregressionComponent,
        pathMatch: 'full',
        data: { reuse: true },
      },
      {
        path: 'forecasts/prophet',
        component: ProphetscenariosComponent,
        pathMatch: 'full',
        data: { reuse: true },
      },
      {
        path: 'forecasts/map',
        component: VarMapComponent,
        pathMatch: 'full',
        data: { reuse: true },
      },
    ]),
    MatCheckboxModule,
    MatTooltipModule,
    NgxMatSelectSearchModule,
    NgScrollbarModule,
  ],
  providers: [
    { provide: RouteReuseStrategy, useClass: RoutecachingService },
    { provide: HTTP_INTERCEPTORS, useClass: AuthService, multi: true },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
