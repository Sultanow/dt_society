import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { GraphData } from 'src/app/types/GraphData';
import { Selections } from 'src/app/types/Datasets';
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

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      if (this.selections.datasets.length > 0) {
        const selectedDatasetId = this.selections.selectedDataset;

        const selectedDatasetIdx = this.selections.datasets.findIndex(
          (dataset) => dataset.id == selectedDatasetId
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
              this.selections.datasets[selectedDatasetIdx].featureOptions !==
              this.oldSelections?.datasets[selectedDatasetIdx].featureSelected
            ) {
              this.dataService
                .getData(
                  this.selections.datasets[selectedDatasetIdx],
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
      this.oldSelections = structuredClone(this.selections);
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
