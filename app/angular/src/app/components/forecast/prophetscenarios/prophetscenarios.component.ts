import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import {
  ActiveScenarios,
  ColumnValues,
  Plot,
  ProphetForecast,
  Scenarios,
} from 'src/app/types/GraphData';
import { faChartLine } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-prophetscenarios',
  templateUrl: './prophetscenarios.component.html',
  styleUrls: ['./prophetscenarios.component.css'],
})
export class ProphetscenariosComponent implements OnInit {
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
      margin: { t: 15, b: 50 },
      height: 300,
    },
    config: { responsive: true },
  };

  public dataScenarios: Plot = {
    data: [],
    layout: {
      legend: { title: { text: '' } },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      title: '',
      margin: {
        t: 10,
        b: 50,
      },
      height: 300,
    },
    config: { responsive: true },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;

  public countries: string[] = [];

  public selectedCountry?: string;

  public scenarioIndeces: number[] = [];

  public predictionPeriods: number = 5;

  public frequency: string = 'Yearly';

  public scenarios: Scenarios = {};

  public dependentDataset?: string;

  public faChartLine = faChartLine;

  public maxScenarios = 5;

  public activeScenarios: ActiveScenarios = {};

  public showSpinner: boolean = false;

  updateMaxScenarios() {
    this.predictionPeriods += 5;
    this.updateScenarios();
  }

  updateScenarios() {
    this.scenarioIndeces = new Array(this.predictionPeriods)
      .fill(null)
      .map((_, i) => i);

    for (const dataset of this.selections.datasets) {
      if (dataset.id !== undefined) {
        if (!(dataset.id in this.scenarios)) {
          this.scenarios[dataset.id] = new Array(this.predictionPeriods).fill(
            null
          );
          this.activeScenarios[dataset.id] = true;
        } else {
          if (this.predictionPeriods > this.scenarios[dataset.id].length) {
            let newScenarios = new Array(
              this.predictionPeriods - this.scenarios[dataset.id].length
            ).fill(null);
            this.scenarios[dataset.id].push(...newScenarios);
          } else {
            this.scenarios[dataset.id].splice(this.predictionPeriods);
          }
        }
      }
    }
  }

  createProphetForecast(data: ProphetForecast) {
    if (this.data.data.length > 0) {
      this.data.data = [];
      this.dataScenarios.data = [];
    }

    const dependentDatasetIdx = this.selections.datasets.findIndex(
      (dataset) => dataset.id == this.dependentDataset
    );
    let forecastHistory: any = {
      type: 'scatter',
      mode: 'lines',
      y: data['merge'][
        this.selections.datasets[dependentDatasetIdx].featureSelected || ''
      ],
      x: data['merge']['x'],
      name: this.selections.datasets[dependentDatasetIdx].featureSelected,
      line: { color: 'mediumpurple' },
    };

    const uncertaintyUpper = data['forecast']['yhat_upper'].map(
      (x, i) => x - data['forecast']['yhat'][i]
    );

    const uncertaintyLower = data['forecast']['yhat'].map(
      (x, i) => x - data['forecast']['yhat_lower'][i]
    );

    let forecastData: any = {
      type: 'scatter',
      mode: 'lines+markers',
      marker: {
        symbol: 'triangle-up',
      },
      line: { dash: 'dash', color: 'mediumpurple' },
      x: data['forecast']['x'],
      y: data['forecast']['yhat'],
      error_y: {
        type: 'data',
        symmetric: false,
        array: uncertaintyUpper,
        arrayminus: uncertaintyLower,
      },
      name: 'Forecast',
    };

    const fillerX = [data['merge']['x'].slice(-1)[0], data['forecast']['x'][0]];

    let filler: any = {
      type: 'scatter',
      mode: 'lines',
      line: { dash: 'dash', color: 'mediumpurple' },
      x: fillerX,
      y: [
        data['merge'][
          this.selections.datasets[dependentDatasetIdx].featureSelected || ''
        ].slice(-1)[0],
        data['forecast']['yhat'][0],
      ],
      showlegend: false,
    };
    this.data.layout['xaxis'] = {
      gridcolor: 'rgba(80, 103, 132, 0.3)',
      title: 'Time',
    };
    this.data.layout['yaxis'] = {
      gridcolor: 'rgba(80, 103, 132, 0.3)',
      title: this.selections.datasets[dependentDatasetIdx].featureSelected,
    };
    // forecast plot
    this.data.data.push(forecastHistory);
    this.data.data.push(forecastData);
    this.data.data.push(filler);

    // scenario plots

    const colors = ['mediumspringgreen', 'hotpink', 'mediumblue', 'goldenrod'];

    var indexFeatures = 0;

    this.dataScenarios.layout.grid = {
      rows: 1,
      columns:
        Object.values(this.activeScenarios).filter(
          (isActive) => isActive === true
        ).length - 1,
      pattern: 'independent',
    };

    for (const [key, value] of Object.entries(data['future'])) {
      if (key === 'x') {
        continue;
      }
      let trace_solid: any = {
        type: 'scatter',
        mode: 'lines',
        line: { color: colors[indexFeatures] },
        name: key,
      };

      let trace_dashed: any = {
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'dash', color: colors[indexFeatures] },
        name: 'Scenario',
      };

      trace_solid.x = data['merge']['x'];
      trace_solid.y = data['merge'][key];

      trace_dashed.x = data['future']['x'];
      trace_dashed.y = data['future'][key];

      if (indexFeatures > 0) {
        trace_solid.xaxis = 'x' + (indexFeatures + 1).toString();
        trace_solid.yaxis = 'y' + (indexFeatures + 1).toString();
        trace_dashed.xaxis = 'x' + (indexFeatures + 1).toString();
        trace_dashed.yaxis = 'y' + (indexFeatures + 1).toString();

        this.dataScenarios.layout['xaxis' + (indexFeatures + 1).toString()] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: 'Time',
        };
        this.dataScenarios.layout['yaxis' + (indexFeatures + 1).toString()] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: key,
        };
      } else {
        this.dataScenarios.layout['xaxis'] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: 'Time',
        };
        this.dataScenarios.layout['yaxis'] = {
          gridcolor: 'rgba(80, 103, 132, 0.3)',
          title: key,
        };
      }

      indexFeatures++;
      this.dataScenarios.data.push(trace_solid);
      this.dataScenarios.data.push(trace_dashed);
    }
  }

  updateProphetForecast() {
    if (
      this.selections.datasets.length > 0 &&
      this.selectedCountry != undefined
    ) {
      if (
        !this.selections.datasets.some(
          (dataset) =>
            dataset.geoSelected === undefined ||
            dataset.timeSelected === undefined ||
            dataset.featureSelected === undefined
        )
      ) {
        const activeScenarios = Object.entries(this.scenarios).filter(
          ([key]) => this.activeScenarios[key] === true
        );

        this.data.data = [];
        this.dataScenarios.data = [];
        this.showSpinner = true;
        this.dataService
          .getData(this.selections.datasets, '/forecast/prophet', {
            country: this.selectedCountry,
            periods: this.predictionPeriods,
            frequency: this.frequency,
            scenarios: Object.fromEntries(activeScenarios),
            dependentDataset: this.dependentDataset,
          })
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.createProphetForecast(event.body as ProphetForecast);
                this.showSpinner = false;
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
      if (this.selections.datasets.length > 0) {
        this.dependentDataset = this.selections.datasets[0].id;
      }
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
        this.updateScenarios();
      }
    });
  }
}
