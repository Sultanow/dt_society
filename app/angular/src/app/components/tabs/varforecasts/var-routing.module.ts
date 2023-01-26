import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { VarMapComponent } from '../../forecast/var-map/var-map.component';
import { VectorautoregressionComponent } from '../../forecast/vectorautoregression/vectorautoregression.component';

const appRoutes: Routes = [
  {
    path: '',
    children: [
      {
        path: '',
        pathMatch: 'full',
        component: VectorautoregressionComponent,
        data: { reuse: true },
      },
      {
        path: 'map',
        pathMatch: 'full',
        component: VarMapComponent,
        data: { reuse: true },
      },
      {
        path: '**',
        redirectTo: '',
        pathMatch: 'full',
      },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(appRoutes)],
  exports: [RouterModule],
})
export class VarRoutingModule {}
