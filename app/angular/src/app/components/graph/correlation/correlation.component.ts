import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
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
        if (
          !this.selections.datasets.some(
            (dataset) =>
              dataset.geoSelected === undefined ||
              dataset.timeSelected === undefined
          )
        ) {
          this.dataService
            .getData(this.selections.datasets, '/graph/corr')
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
    this.oldSelections = structuredClone(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
