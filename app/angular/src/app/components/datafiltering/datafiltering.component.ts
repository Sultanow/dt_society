import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { SelectedDatasets, AvailableDatasets, DatasetOptions } from '../../Datasets'
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-datafiltering',
  templateUrl: './datafiltering.component.html',
  styleUrls: ['./datafiltering.component.css']
})
export class DatafilteringComponent implements OnInit {

  constructor(private httpClient: HttpClient) { }

  @Output() columnsUpdatedEvent = new EventEmitter<any>();

  selectedDatasets: SelectedDatasets = {
    datasets: []
  }

  availableDatasets: AvailableDatasets = {
    datasets: []
  }

  updateSelectedColumns(filename: string, value: string, column: string) {
    if (this.selectedDatasets.datasets != undefined) {
      const datasetIndex = this.selectedDatasets.datasets.map(d => d.datasetId).indexOf(filename)

      switch (column) {
        case "geo":
          this.selectedDatasets.datasets[datasetIndex].geoColumn = value;
          break;
        case "rshp":
          this.selectedDatasets.datasets[datasetIndex].reshapeColumn = value;
          break;
        case "x":
          this.selectedDatasets.datasets[datasetIndex].timeColumn = value;
          break;
        case "y":
          this.selectedDatasets.datasets[datasetIndex].featureColumn = value;
      }

      this.columnsUpdatedEvent.emit(this.selectedDatasets)
    }
  }

  ngOnInit(): void {
    this.httpClient.get("http://127.0.0.1:5000/datasets").subscribe(availableDatasets => {
      this.availableDatasets.datasets = (availableDatasets as DatasetOptions[]);
      if (this.selectedDatasets.datasets != undefined) {
        //console.log(this.availableDatasets)

        for (const dataset of this.availableDatasets.datasets) {
          if (this.selectedDatasets.datasets.filter(d => d.datasetId == dataset.datasetId).length == 0) {
            this.selectedDatasets.datasets.push({ datasetId: dataset.datasetId });
          }
        }
      }
      // console.log(this.selectedDatasets)
      // console.log(this.availableDatasets)
    })
  }

}
