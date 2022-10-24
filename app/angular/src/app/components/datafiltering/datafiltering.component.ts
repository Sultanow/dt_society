import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Selections } from '../../types/Datasets';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-datafiltering',
  templateUrl: './datafiltering.component.html',
  styleUrls: ['./datafiltering.component.css'],
})
export class DatafilteringComponent implements OnInit {
  constructor(private dataService: DataService) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  reshape: boolean = false;

  fileName = '';

  updateSelectedColumns(
    filename: string | undefined,
    value: string,
    column: string
  ) {
    if (this.selections.datasets.length > 0) {
      const datasetIndex = this.selections.datasets
        .map((d) => d.id)
        .indexOf(filename);

      switch (column) {
        case 'geo':
          this.selections.datasets[datasetIndex].geoSelected = value;
          break;
        case 'rshp':
          this.selections.datasets[datasetIndex].reshapeSelected = value;
          this.dataService.getReshapedData(
            this.selections,
            filename,
            this.reshape
          );
          break;
        case 'x':
          this.selections.datasets[datasetIndex].timeSelected = value;
          break;
        case 'y':
          this.selections.datasets[datasetIndex].featureSelected = value;
      }

      this.dataService.updateDatasetsSelection(this.selections);
    }
  }

  onFileUpload(event: any) {
    this.dataService.uploadDataset(event, this.selections);
  }

  onDeleteFile(datasedId: string | undefined) {
    this.dataService.deleteDataset(datasedId, this.selections);
  }

  reshapeOptions(datasetId: string | undefined, reshape: boolean): void {
    this.reshape = reshape;
    this.dataService.getReshapedData(this.selections, datasetId, this.reshape);
    this.dataService.updateDatasetsSelection(this.selections);
  }

  changeFocus() {
    this.dataService.updateDatasetsSelection(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });

    this.dataService.getAvailableDatasets(this.selections);
  }
}
