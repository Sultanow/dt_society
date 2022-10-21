import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { SelectedDatasets } from 'src/app/types/Datasets';
import { GraphData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-correlation',
  styleUrls: ['./correlation.component.css'],
  templateUrl: './correlation.component.html',
})
export class CorrelationComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: GraphData = {
    data: [],
    layout: {},
  };

  public selectedDatasets: SelectedDatasets = {
    datasets: [],
  };

  private oldSelectedDatasets?: SelectedDatasets;

  ngDoCheck() {
    if (
      JSON.stringify(this.selectedDatasets) !==
      JSON.stringify(this.oldSelectedDatasets)
    ) {
      if (this.selectedDatasets.datasets.length > 0) {
        if (
          !this.selectedDatasets.datasets.some(
            (dataset) =>
              dataset.geoColumn === undefined ||
              dataset.timeColumn === undefined
          )
        ) {
          this.dataService
            .getData(this.selectedDatasets.datasets, '/graph/corr')
            .subscribe((event) => {
              if (event.type === HttpEventType.Response) {
                if (event.body) {
                  this.data.data = event.body.data;
                  this.data.layout = event.body.layout;
                }
              }
            });
        }
      }
    }
    this.oldSelectedDatasets = structuredClone(this.selectedDatasets);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
  }
}
