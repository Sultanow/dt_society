import { HttpEventType } from '@angular/common/http';
import { Component, Input, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
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

  public selectedDatasets: SelectedDatasets = {
    datasets: [],
  };

  public features = {
    availableFeatures: [],
  };

  selectedFeaturesControl = new FormControl('');
  private oldSelectedDatasets?: SelectedDatasets;
  public selectedFeatures: string | null = null;

  ngDoCheck() {
    if (
      JSON.stringify(this.selectedDatasets) !==
      JSON.stringify(this.oldSelectedDatasets)
    ) {
      const oldFeature = this.oldSelectedDatasets?.datasets;

      if (this.selectedDatasets.datasets.length > 0) {
        if (
          !this.selectedDatasets.datasets.some(
            (dataset) =>
              dataset.geoColumn === undefined ||
              dataset.timeColumn === undefined
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
    this.oldSelectedDatasets = structuredClone(this.selectedDatasets);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
    this.selectedFeaturesControl.valueChanges.subscribe((value) => {
      this.selectedFeatures = value;
    });
  }
}
