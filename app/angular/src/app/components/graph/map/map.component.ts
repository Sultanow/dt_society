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

  ngOnChanges(changes: SimpleChange) {
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
          this.showSpinner = true;
          this.dataService
            .getData(indexFocus, '/graph/map')
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

  ngOnInit(): void {}
}
