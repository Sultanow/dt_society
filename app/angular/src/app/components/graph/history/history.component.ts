import {
  Component,
  Input,
  OnInit,
  OnChanges,
  SimpleChange,
} from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { GraphData } from 'src/app/types/GraphData';
import { SelectedDatasets } from 'src/app/types/Datasets';
import { HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
})
export class HistoryComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: GraphData = {
    data: [],
    layout: {},
  };

  public selectedDatasets: SelectedDatasets = {
    datasets: [],
    inFocusDataset: undefined,
  };

  private oldSelectedDatasets?: SelectedDatasets;

  ngDoCheck() {
    if (
      JSON.stringify(this.selectedDatasets) !==
      JSON.stringify(this.oldSelectedDatasets)
    ) {
      if (this.selectedDatasets.datasets.length > 0) {
        const selectedDatasetId = this.selectedDatasets.inFocusDataset;

        const selectedDatasetIdx = this.selectedDatasets.datasets.findIndex(
          (dataset) => dataset.datasetId == selectedDatasetId
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
              this.dataService
                .getData(
                  this.selectedDatasets.datasets[selectedDatasetIdx],
                  '/graph/history'
                )
                .subscribe((data) => {
                  if (data.type === HttpEventType.Response) {
                    if (data.body) {
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
