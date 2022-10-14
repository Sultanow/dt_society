import { Component, Output } from '@angular/core';
import { SelectedDatasets } from './Datasets';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'angular';

  selectedDatasets: SelectedDatasets = {
    datasets: []
  }

  getSelection(columns: SelectedDatasets) {

    let datasets = columns.datasets
    this.selectedDatasets = { datasets }
  }
}
