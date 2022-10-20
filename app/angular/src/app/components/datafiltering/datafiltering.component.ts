import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import {
  SelectedDatasets,
  AvailableDatasets,
  DatasetOptions,
} from '../../types/Datasets';
import { HttpClient } from '@angular/common/http';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-datafiltering',
  templateUrl: './datafiltering.component.html',
  styleUrls: ['./datafiltering.component.css'],
})
export class DatafilteringComponent implements OnInit {
  constructor(
    private httpClient: HttpClient,
    private dataService: DataService
  ) {}

  @Output() columnsUpdatedEvent = new EventEmitter<any>();

  selectedDatasets: SelectedDatasets = {
    datasets: [],
  };
  availableDatasets: AvailableDatasets = {
    datasets: [],
  };

  reshape: boolean = false;

  fileName = '';

  inFocus: string | undefined;

  updateSelectedColumns(filename: string, value: string, column: string) {
    if (this.selectedDatasets.datasets != undefined) {
      const datasetIndex = this.selectedDatasets.datasets
        .map((d) => d.datasetId)
        .indexOf(filename);

      switch (column) {
        case 'geo':
          this.selectedDatasets.datasets[datasetIndex].geoColumn = value;
          break;
        case 'rshp':
          this.selectedDatasets.datasets[datasetIndex].reshapeColumn = value;
          this.dataService.getReshapedData(
            this.availableDatasets,
            this.selectedDatasets,
            filename,
            this.reshape
          );
          break;
        case 'x':
          this.selectedDatasets.datasets[datasetIndex].timeColumn = value;
          break;
        case 'y':
          this.selectedDatasets.datasets[datasetIndex].featureColumn = value;
      }

      this.dataService.updateSelectedDataset(this.selectedDatasets);
    }
  }

  onFileUpload(event: any) {
    this.dataService.uploadDataset(
      event,
      this.availableDatasets,
      this.selectedDatasets,
      this.inFocus
    );
  }

  onDeleteFile(datasedId: string) {
    this.dataService.deleteDataset(
      datasedId,
      this.availableDatasets,
      this.selectedDatasets
    );
  }

  reshapeOptions(datasetId: string, reshape: boolean): void {
    this.reshape = reshape;
    this.dataService.getReshapedData(
      this.availableDatasets,
      this.selectedDatasets,
      datasetId,
      this.reshape
    );
  }

  changeFocus() {
    this.selectedDatasets.inFocusDataset = this.inFocus;
    this.dataService.updateSelectedDataset(this.selectedDatasets);
    //this.columnsUpdatedEvent.emit(this.selectedDatasets);
  }

  ngOnInit(): void {

    this.dataService.currentSelections.subscribe((value) => { this.selectedDatasets = value;});
    console.log("DataFilter subject setup");
    console.log(this.selectedDatasets);

    this.dataService.getAvailableDatasets(
      this.availableDatasets,
      this.selectedDatasets,
      this.inFocus
    );
  }
}
