import { HttpEventType } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { SelectedDatasets } from 'src/app/types/Datasets';
import { GraphData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-heatmap',
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css'],
})
export class HeatmapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: GraphData = {
    data: [],
    layout: {},
  };

  @Input()
  public selectedDatasets: SelectedDatasets = {
    datasets: [],
  };

  ngOnChanges() {
    if (this.selectedDatasets.datasets.length > 0) {
      if (
        !this.selectedDatasets.datasets.some(
          (dataset) =>
            dataset.geoColumn === undefined || dataset.timeColumn === undefined
        )
      ) {
        this.dataService
          .getData(this.selectedDatasets.datasets, '/graph/heatmap')
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

  ngOnInit(): void {}
}
