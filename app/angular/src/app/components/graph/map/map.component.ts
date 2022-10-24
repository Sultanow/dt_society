import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { map } from 'rxjs';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { CountryData, GraphData, MapPlot, Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-map',
  styleUrls: ['./map.component.css'],
  templateUrl: './map.component.html',
})
export class MapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: MapPlot = {
    data: [],
    layout: {
      geo: { scope: 'europe' },
    },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  showSpinner: boolean = false;

  private oldSelections?: Selections;

  createMapPlot(data: CountryData, selectedIdx: number) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let mapData: any = {
      type: 'choropleth',
      locations: [],
      z: [],
      autocolorscale: true,
    };

    for (const [key, value] of Object.entries(data)) {
      const timeSelected = this.selections.datasets[selectedIdx].timeSelected;
      const featureSelected =
        this.selections.datasets[selectedIdx].featureSelected;
      if (timeSelected !== undefined && featureSelected !== undefined) {
        mapData.locations.push(key);
        mapData.z.push(value[featureSelected][0]);
      }
    }

    this.data.data.push(mapData);
  }

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
                      // this.data.data = data.body.data;
                      // this.data.layout = data.body.layout;
                      this.createMapPlot(data.body as any, selectedDatasetIdx);
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
