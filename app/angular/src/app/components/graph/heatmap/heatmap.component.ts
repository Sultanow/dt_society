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

  public data: Plot = {
    data: [],
    layout: {
      legend: { title: { text: 'Pearson r' } },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
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

  private oldSelections?: Selections;
  public selectedFeatures?: string | null;

  createHeatmapPlot(data: CorrelationMatrix) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let heatmap: any = {};

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
      if (
        !this.selections.datasets.some(
          (dataset) =>
            dataset.geoSelected === undefined ||
            dataset.timeSelected === undefined
        )
      ) {
        this.dataService
          .getData(this.selections.datasets, '/graph/heatmap', {
            features: this.selectedFeatures,
            country: this.selections.selectedCountry,
          })
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.createHeatmapPlot(event.body as CorrelationMatrix);
              }
            }
          });
      }
    }
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
    }
    this.oldSelections = structuredClone(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      if (this.featureOptions.length > 0) {
        this.featureOptions = [];
      }

      this.updateFeatureOptions(this.selections.selectedCountry);
      let currentFeatureSelection = this.selectionControl
        .get('selectedFeaturesControl')!
        .getRawValue();
      if (currentFeatureSelection !== null) {
        let newSelection = currentFeatureSelection.filter((x: string) =>
          this.featureOptions.includes(x)
        );
        this.selectionControl
          .get('selectedFeaturesControl')!
          .setValue(newSelection);
        this.selectedFeatures = newSelection;
        this.updateHeatmap();
      }
    });

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
  }

  private updateFeatureOptions(selectedCountry: any) {
    this.featureOptions = [];
    for (const dataset of this.selections.datasets) {
      if (
        selectedCountry !== null &&
        dataset.featureOptions !== undefined &&
        dataset.countryOptions?.includes(selectedCountry)
      ) {
        this.featureOptions.push(...dataset.featureOptions);
      }
    }
  }
}
