import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { ColumnValues, Models, Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-vectorautoregression',
  templateUrl: './vectorautoregression.component.html',
  styleUrls: ['./vectorautoregression.component.css'],
})
export class VectorautoregressionComponent implements OnInit {
  constructor(private dataService: DataService) {}

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

  public models: Models = {
    var: 'Vector Auto Regression',
    hwes: 'HW Smoothing',
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  public countries: string[] = [];

  public predictionPeriods: number = 0;

  public maxLags: number = 1;

  public frequency: string = 'Yearly';

  public selectedModel: string = 'var';

  createVarForecast(data: ColumnValues) {
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
      columns: this.selections.datasets.length,
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

  updateVarForecast() {
    if (
      this.selections.datasets.length > 0 &&
      this.selections.selectedCountry != undefined
    ) {
      if (
        !this.selections.datasets.some(
          (dataset) =>
            dataset.geoSelected === undefined ||
            dataset.timeSelected === undefined ||
            dataset.featureSelected === undefined
        )
      ) {
        this.dataService
          .getData(
            this.selections.datasets,
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
                this.createVarForecast(event.body as ColumnValues);
              }
            }
          });
      }
    }
  }

  updateParameterSlider(event: any) {
    switch (event) {
      case 'hwes':
        this.maxLags = 0.49;
        break;
      case 'var':
        this.maxLags = 1;
        break;
    }
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      this.updateVarForecast();
    }
    this.oldSelections = structuredClone(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;

      var countries: string[] | undefined = [] || undefined;

      if (this.selections.datasets.length > 0) {
        for (const data of this.selections.datasets) {
          countries = [...countries, ...(data.countryOptions || [])];
        }

        this.countries = [...new Set(countries)];
      }
    });
  }
}
