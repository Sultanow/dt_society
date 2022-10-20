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
      this.oldSelectedDatasets = structuredClone(this.selectedDatasets);
      if (this.selectedDatasets.datasets.length > 0) {
        const datasetId = this.selectedDatasets.inFocusDataset;

        const indexFocus = this.selectedDatasets.datasets.find(
          (dataset) => dataset.datasetId == datasetId
        );

        if (indexFocus !== undefined) {
          if (
            indexFocus.geoColumn !== undefined &&
            indexFocus.reshapeColumn !== undefined &&
            indexFocus.featureColumn !== undefined &&
            indexFocus.timeColumn !== undefined
          ) {
            this.dataService
              .getData(indexFocus, '/graph/history')
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
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
  }
}
