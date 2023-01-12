import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CorrelationsComponent } from './components/tabs/correlations/correlations.component';
import { ProphetscenariosComponent } from './components/forecast/prophetscenarios/prophetscenarios.component';
import { VarMapComponent } from './components/forecast/var-map/var-map.component';
import { VectorautoregressionComponent } from './components/forecast/vectorautoregression/vectorautoregression.component';
import { OverviewComponent } from './components/tabs/overview/overview.component';
import { VarforecastsComponent } from './components/tabs/varforecasts/varforecasts.component';

const appRoutes: Routes = [
  {
    path: '',
    redirectTo: 'overview',
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
    component: VarforecastsComponent,
    children: [
      {
        path: '',
        pathMatch: 'full',
        redirectTo: 'graph',
      },
      {
        path: 'graph',
        component: VectorautoregressionComponent,
        data: { reuse: true },
      },
      {
        path: 'map',
        component: VarMapComponent,
        data: { reuse: true },
      },
      {
        path: '**',
        redirectTo: 'graph',
        pathMatch: 'full',
      },
    ],
  },
  {
    path: 'forecasts/prophet',
    component: ProphetscenariosComponent,
    pathMatch: 'full',
    data: { reuse: true },
  },
  {
    path: '**',
    redirectTo: 'overview',
    pathMatch: 'full',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(appRoutes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
