import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import {
  ActiveScenarios,
  ColumnValues,
  Models,
  Plot,
} from 'src/app/types/GraphData';

@Component({
  selector: 'app-vectorautoregression',
  templateUrl: './vectorautoregression.component.html',
  styleUrls: ['./vectorautoregression.component.css'],
})
export class VectorautoregressionComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public models: Models = {
    var: 'Vector Auto Regression',
    hwes: 'HW Smoothing',
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  // Binded properties
  public countries: string[] = [];
  public predictionPeriods: number = 0;
  public maxLags: number = 1;
  public frequency: string = 'Yearly';
  public selectedModel: string = 'var';
  public showSpinner: boolean = false;
  public validDatasets: number = 0;
  public selectableDatasets: ActiveScenarios = {};
  public activeDatasets: ActiveScenarios = {};
  public data: Plot = {
    data: [],
    layout: {
      legend: { title: { text: '' } },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      title: '',
    },
    config: { responsive: true },
  };

  createVarForecast(data: ColumnValues): void {
    // Renders plot from received data
    if (this.data.data.length > 0) {
      this.data.data = [];
    }
    this.data.layout.title =
      this.models[this.selectedModel] +
      ' (' +
      this.selections.selectedCountry +
      ')';
    this.data.layout.grid = {
      rows: 1,
      columns: Object.keys(data).length - 1,
      pattern: 'independent',
    };

    const colors = [
      'mediumpurple',
      'mediumspringgreen',
      'hotpink',
      'mediumblue',
      'goldenrod',
    ];
    var i = 0;
    for (const [key, value] of Object.entries(data)) {
      if (key === 'x') {
        continue;
      }
      let trace_solid: any = {
        type: 'scatter',
        mode: 'lines',
        line: { color: colors[i] },
      };

      let trace_dashed: any = {
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'dash', color: colors[i] },
      };

      if (this.predictionPeriods > 0) {
        trace_solid.y = value.slice(0, -this.predictionPeriods);
        trace_solid.x = data['x'].slice(0, -this.predictionPeriods);
        trace_solid.name = key;

        trace_dashed.y = value.slice(-this.predictionPeriods - 1);
        trace_dashed.x = data['x'].slice(-this.predictionPeriods - 1);
        trace_dashed.name = key + ' Prediction';
      } else {
        trace_solid.y = value;
        trace_solid.x = data['x'];
        trace_solid.name = key;
      }

      if (i > 0) {
        trace_solid.xaxis = 'x' + (i + 1).toString();
        trace_solid.yaxis = 'y' + (i + 1).toString();
        trace_dashed.xaxis = 'x' + (i + 1).toString();
        trace_dashed.yaxis = 'y' + (i + 1).toString();

        this.data.layout['xaxis' + (i + 1).toString()] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: 'Time',
        };
        this.data.layout['yaxis' + (i + 1).toString()] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: key,
        };
      } else {
        this.data.layout['xaxis'] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: 'Time',
        };
        this.data.layout['yaxis'] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: key,
        };
      }
      i++;
      this.data.data.push(trace_solid);
      this.data.data.push(trace_dashed);
    }
  }

  toggleSpinner(): void {
    this.showSpinner = !this.showSpinner;
  }

  updateVarForecast(): void {
    // Handles updates updates of VAR forecast
    if (
      this.selections.datasets.length > 0 &&
      this.selections.selectedCountry != undefined
    ) {
      const filteredSelections = this.selections.datasets.filter(
        (dataset) =>
          dataset.featureSelected !== undefined &&
          dataset.timeSelected !== undefined &&
          dataset.countryOptions?.includes(
            this.selections.selectedCountry as string
          ) &&
          this.activeDatasets[dataset.id as string] === true
      );
      if (filteredSelections.length > 1) {
        this.toggleSpinner();
        this.dataService
          .getData(
            filteredSelections,
            '/forecast/multivariate/' + this.selectedModel,
            {
              country: this.selections.selectedCountry,
              periods: this.predictionPeriods,
              maxLags: this.maxLags,
              frequency: this.frequency,
            }
          )
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.toggleSpinner();
                this.createVarForecast(event.body as ColumnValues);
              }
            }
          });
      }
    }
  }

  updateParameterSlider(event: any): void {
    switch (event) {
      case 'hwes':
        this.maxLags = 0.49;
        break;
      case 'var':
        this.maxLags = 1;
        break;
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((updatedSelections) => {
      this.selections = updatedSelections;
      this.validDatasets = 0;

      if (this.selections.datasets.length > 0) {
        let countries = this.selections.datasets.reduce<string[]>(
          (countries, dataset) => {
            if (
              dataset.countryOptions?.includes(this.selections.selectedCountry!)
            ) {
              this.validDatasets++;
            }
            if (
              !Object.keys(this.activeDatasets).includes(dataset.id as string)
            ) {
              this.activeDatasets[dataset.id as string] = true;
            } else {
              this.selectableDatasets[dataset.id as string] =
                dataset.countryOptions?.includes(
                  this.selections.selectedCountry as string
                ) as boolean;

              this.activeDatasets[dataset.id as string] =
                dataset.countryOptions?.includes(
                  this.selections.selectedCountry as string
                ) as boolean;
            }
            return [...countries, ...(dataset.countryOptions || [])];
          },
          []
        );

        this.countries = [...new Set(countries)];
      }
      this.updateVarForecast();
    });
  }
}
