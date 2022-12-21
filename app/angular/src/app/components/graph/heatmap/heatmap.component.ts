import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { CorrelationMatrix, Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-heatmap',
  templateUrl: './heatmap.component.html',
  styleUrls: ['./heatmap.component.css'],
})
export class HeatmapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public showSpinner: boolean = false;

  public data: Plot = {
    data: [],
    layout: {
      legend: { title: { text: 'Pearson r' } },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      margin: { t: 10, b: 50 },
    },
    config: { responsive: true },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  public featureOptions: string[] = [];

  selectionControl = new FormGroup({
    selectedFeaturesControl: new FormControl(),
  });

  countries: (undefined | string[] | string)[] = [];

  public selectedFeatures?: string | null;
  public matchingFrequencies?: boolean;

  createHeatmapPlot(data: CorrelationMatrix) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let heatmap: any = {};

    this.matchingFrequencies = data.matchingFrequencies;

    let replacedZeroes = data.matrix.map((row) =>
      row.map((value) => {
        if (value === 0) {
          return null;
        }
        return value;
      })
    );

    heatmap.z = replacedZeroes.reverse();
    heatmap.x = data.columns;
    heatmap.y = data.columns.slice().reverse();
    heatmap.type = 'heatmap';
    heatmap.colorscale = 'Viridis';
    heatmap.colorbar = { title: 'Pearson r' };

    this.data.data.push(heatmap);
  }

  updateHeatmap() {
    if (
      this.selections.datasets.length > 0 &&
      this.selectedFeatures !== undefined &&
      this.selectedFeatures!.length > 1
    ) {
      this.showSpinner = true;
      const filteredSelections = this.selections.datasets.filter(
        (dataset) =>
          dataset.featureSelected !== undefined &&
          dataset.timeSelected !== undefined
      );
      this.dataService
        .getData(filteredSelections, '/graph/heatmap', {
          features: this.selectedFeatures,
          country: this.selections.selectedCountry,
        })
        .subscribe((event) => {
          if (event.type === HttpEventType.Response) {
            if (event.body) {
              this.createHeatmapPlot(event.body as CorrelationMatrix);
              this.showSpinner = false;
            }
          }
        });
    }
  }

  ngOnInit(): void {
    this.selectionControl
      .get('selectedFeaturesControl')!
      .valueChanges.subscribe((selectedFeatures) => {
        if (
          this.selectionControl
            .get('selectedFeaturesControl')!
            .getRawValue() !== ''
        ) {
          this.selectedFeatures = selectedFeatures;
          this.updateHeatmap();
        }
      });

    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      if (this.featureOptions.length > 0) {
        this.featureOptions = [];
      }

      this.updateFeatureOptions();

      this.selectionControl
        .get('selectedFeaturesControl')!
        .setValue(this.featureOptions);
    });
  }

  private updateFeatureOptions() {
    this.featureOptions = [];
    for (const dataset of this.selections.datasets) {
      if (
        dataset.featureOptions !== undefined &&
        ((this.selections.selectedCountry !== (undefined && null) &&
          dataset.countryOptions?.includes(
            this.selections.selectedCountry?.toString()
          )) ||
          dataset.countryOptions === undefined) &&
        dataset.featureSelected !== undefined &&
        dataset.timeSelected !== undefined
      ) {
        this.featureOptions.push(
          ...dataset.featureOptions.filter(
            (feature) => feature !== dataset.timeSelected
          )
        );
      }
    }
  }
}
