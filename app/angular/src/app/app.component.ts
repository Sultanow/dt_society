import { Component, Output } from '@angular/core';
import {
  AvailableDatasets,
  DatasetOptions,
  SelectedDatasets,
} from './types/Datasets';

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

  features = {
    availableFeatures: Array(),
  };

  // getSelection(columns: SelectedDatasets) {
  //   let datasets = columns.datasets;
  //   let inFocusDataset = columns.inFocusDataset;
  //   this.selectedDatasets = { datasets, inFocusDataset };
  // }

  getSelection(columns: any) {
    if ('selected' in columns) {
      console.log(columns);
      let datasets: [] = columns.selected.datasets;
      let inFocusDataset: string = columns.selected.inFocusDataset;
      this.selectedDatasets = { datasets, inFocusDataset };

      let features = Array();

      let availableFeatures = (columns.available.datasets as DatasetOptions[])
        .filter((datasets) => datasets.featureOptions !== undefined)
        .map((dataset) => features.concat(dataset.featureOptions))
        .flat();

      this.features = { availableFeatures };
    }
  }
}
