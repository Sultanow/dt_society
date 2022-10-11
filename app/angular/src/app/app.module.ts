import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http'

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HistoryComponent } from './graph/history/history.component';

import * as PlotlyJS from 'plotly.js-dist-min';
import { PlotlyModule } from 'angular-plotly.js';
import { MapComponent } from './graph/map/map.component';
import { HeatmapComponent } from './graph/heatmap/heatmap.component';
import { CorrelationComponent } from './graph/correlation/correlation.component';
import { HwsmoothingComponent } from './forecast/hwsmoothing/hwsmoothing.component';
import { VectorautoregressionComponent } from './forecast/vectorautoregression/vectorautoregression.component';
import { ProphetscenariosComponent } from './forecast/prophetscenarios/prophetscenarios.component';

PlotlyModule.plotlyjs = PlotlyJS;

@NgModule({
  declarations: [
    AppComponent,
    HistoryComponent,
    MapComponent,
    HeatmapComponent,
    CorrelationComponent,
    HwsmoothingComponent,
    VectorautoregressionComponent,
    ProphetscenariosComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    PlotlyModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
