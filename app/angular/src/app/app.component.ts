import { Component, Output } from '@angular/core';
import { SelectedDatasets } from './types/Datasets';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'angular';

  selectedDatasets: SelectedDatasets = {
    datasets: [],
  };

  getSelection(columns: SelectedDatasets) {
    let datasets = columns.datasets;
    let inFocusDataset = columns.inFocusDataset;
    this.selectedDatasets = { datasets, inFocusDataset };
  }
}
