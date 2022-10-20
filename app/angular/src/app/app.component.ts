import { Component, Output } from '@angular/core';
import { SelectedDatasets } from './types/Datasets';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'angular';

  constructor(private dataService: DataService) {}

  selectedDatasets: SelectedDatasets = {
    datasets: [],
  };

  //  getSelection(columns: SelectedDatasets) {
  //     let datasets = columns.datasets;
  //     let inFocusDataset = columns.inFocusDataset;
  //     this.selectedDatasets = { datasets, inFocusDataset };
  //  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
  }
}
