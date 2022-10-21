import { HttpEvent, HttpEventType } from '@angular/common/http';
import { Component, Input, OnInit, SimpleChange } from '@angular/core';
import { Observable } from 'rxjs';
import { DataService } from 'src/app/services/data.service';
import { SelectedDatasets } from 'src/app/types/Datasets';
import { GraphData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-map',
  styleUrls: ['./map.component.css'],
  templateUrl: './map.component.html',
})
export class MapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: GraphData = {
    data: [],
    layout: {},
  };

  @Input()
  public selectedDatasets: SelectedDatasets = {
    datasets: [],
    inFocusDataset: undefined,
  };

  showSpinner: boolean = false;

  private oldSelectedDatasets?: SelectedDatasets;

  ngDoCheck() {
    if (
      JSON.stringify(this.selectedDatasets) !==
      JSON.stringify(this.oldSelectedDatasets)
    ) {
      if (this.selectedDatasets.datasets.length > 0) {
        const datasetId = this.selectedDatasets.inFocusDataset;

        const selectedDatasetIdx = this.selectedDatasets.datasets.findIndex(
          (dataset) => dataset.datasetId == datasetId
        );

        if (this.selectedDatasets.datasets[selectedDatasetIdx] !== undefined) {
          if (
            this.selectedDatasets.datasets[selectedDatasetIdx].geoColumn !==
              undefined &&
            this.selectedDatasets.datasets[selectedDatasetIdx].reshapeColumn !==
              undefined &&
            this.selectedDatasets.datasets[selectedDatasetIdx].featureColumn !==
              undefined &&
            this.selectedDatasets.datasets[selectedDatasetIdx].timeColumn !==
              undefined
          ) {
            if (
              this.selectedDatasets.datasets[selectedDatasetIdx]
                .featureColumn !==
              this.oldSelectedDatasets?.datasets[selectedDatasetIdx]
                .featureColumn
            ) {
              this.showSpinner = true;
              this.dataService
                .getData(
                  this.selectedDatasets.datasets[selectedDatasetIdx],
                  '/graph/map'
                )
                .subscribe((data) => {
                  if (data.type === HttpEventType.DownloadProgress) {
                    console.log('downloading');
                  }

                  if (data.type === HttpEventType.Response) {
                    console.log('completed');
                    if (data.body) {
                      this.showSpinner = false;
                      this.data.data = data.body.data;
                      this.data.layout = data.body.layout;
                    }
                  }
                });
            }
          }
        }
      }
      this.oldSelectedDatasets = structuredClone(this.selectedDatasets);
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
  }
}
