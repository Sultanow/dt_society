import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
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

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  showSpinner: boolean = false;

  private oldSelections?: Selections;

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      if (this.selections.datasets.length > 0) {
        const datasetId = this.selections.selectedDataset;

        const selectedDatasetIdx = this.selections.datasets.findIndex(
          (dataset) => dataset.id == datasetId
        );

        if (this.selections.datasets[selectedDatasetIdx] !== undefined) {
          if (
            this.selections.datasets[selectedDatasetIdx].geoSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].reshapeSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].featureSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].timeSelected !==
              undefined
          ) {
            if (
              this.selections.datasets[selectedDatasetIdx].featureSelected !==
              this.oldSelections?.datasets[selectedDatasetIdx].featureSelected
            ) {
              this.showSpinner = true;
              this.dataService
                .getData(
                  this.selections.datasets[selectedDatasetIdx],
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
      this.oldSelections = structuredClone(this.selections);
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
