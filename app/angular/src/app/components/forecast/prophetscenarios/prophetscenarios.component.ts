import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import {
  Plot,
  ProphetForecast,
  Scenario,
  ScenarioData,
} from 'src/app/types/GraphData';
import { faChartLine } from '@fortawesome/free-solid-svg-icons';
import { Options } from '@angular-slider/ngx-slider';

@Component({
  selector: 'app-prophetscenarios',
  templateUrl: './prophetscenarios.component.html',
  styleUrls: ['./prophetscenarios.component.css'],
})
export class ProphetscenariosComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  // Scenarios
  public scenarioIndeces: number[] = [];
  public scenarioData: ScenarioData = {};

  // Forecast plot
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

  // Scenarios plot
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

  // Bindings
  public selectedMode: string = 'auto';
  public predictionPeriods: number = 5;
  public dependentDataset?: string;
  public faChartLine = faChartLine;
  public maxScenarios = 5;
  public validDatasets: number = 0;
  public showSpinner: boolean = false;
  public currentSliderValue = 0;

  options: Options = {
    floor: 0,
    ceil: 0,
    showTicks: true,
  };

  updateMaxScenarios() {
    this.predictionPeriods += 5;
    this.updateScenarios();
  }

  updateSlider(slidervalues?: string[]) {
    if (slidervalues !== undefined) {
      const newOptions: Options = Object.assign({}, this.options);
      newOptions.floor = 0;
      newOptions.ceil = slidervalues.length - 1;
      newOptions.translate = (value: number) => {
        return String(slidervalues[value]);
      };
      this.options = newOptions;
    } else {
      const newOptions: Options = Object.assign({}, this.options);
      newOptions.floor = 0;
      newOptions.ceil = 40;
      newOptions.translate = (value: number) => {
        return String(value);
      };
      this.options = newOptions;
    }
  }

  updateScenarios() {
    this.scenarioIndeces = new Array(this.predictionPeriods)
      .fill(null)
      .map((_, i) => i);

    for (const dataset of this.selections.datasets) {
      if (dataset.id !== undefined) {
        if (!(dataset.id in this.scenarioData)) {
          this.scenarioData[dataset.id] = {} as Scenario;
          this.scenarioData[dataset.id].data = new Array(
            this.predictionPeriods
          ).fill(null);
          this.scenarioData[dataset.id].active = true;
        } else {
          if (
            this.predictionPeriods > this.scenarioData[dataset.id].data.length
          ) {
            let newScenarios = new Array(
              this.predictionPeriods - this.scenarioData[dataset.id].data.length
            ).fill(null);
            this.scenarioData[dataset.id].data.push(...newScenarios);
          } else {
            this.scenarioData[dataset.id].data.splice(this.predictionPeriods);
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

    if (data.slidervalues !== undefined) {
      this.updateSlider(data.slidervalues);
    } else {
      this.updateSlider();
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
        Object.keys(this.scenarioData).filter(
          (id) => this.scenarioData[id].active === true
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
      this.selections.selectedCountry != undefined
    ) {
      const activeScenarios = Object.fromEntries(
        Object.entries(this.scenarioData).filter(
          ([id, scenario]) => scenario.active
        )
      );

      const activeSelections = this.selections.datasets.filter((dataset) =>
        Object.keys(activeScenarios).includes(dataset.id as string)
      );

      if (Object.keys(activeScenarios).length > 1) {
        this.data.data = [];
        this.dataScenarios.data = [];
        this.showSpinner = true;

        if (this.selectedMode == 'custom') {
          this.dataService
            .getData(activeSelections, '/forecast/prophet', {
              country: this.selections.selectedCountry,
              periods: this.predictionPeriods,
              scenarios: activeScenarios,
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
        } else {
          this.dataService
            .getData(activeSelections, '/forecast/prophet', {
              country: this.selections.selectedCountry,
              predictions: this.currentSliderValue,
              scenarios: activeScenarios,
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
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      this.validDatasets = 0;

      if (this.selections.datasets.length > 0) {
        if (this.dependentDataset === undefined) {
          this.dependentDataset = this.selections.datasets[0].id;
        }

        this.updateScenarios();

        for (const dataset_id of Object.keys(this.scenarioData)) {
          let selectedDataset = this.selections.datasets.filter(
            (dataset) => dataset.id === dataset_id
          )[0];

          if (
            selectedDataset.countryOptions?.includes(
              this.selections.selectedCountry!
            )
          ) {
            this.validDatasets++;
          }

          this.scenarioData[dataset_id].selectable =
            selectedDataset.countryOptions?.includes(
              this.selections.selectedCountry as string
            ) as boolean;

          this.scenarioData[dataset_id].active =
            selectedDataset.countryOptions?.includes(
              this.selections.selectedCountry as string
            ) as boolean;
        }

        const selectabelDependentDatasets = Object.keys(
          this.scenarioData
        ).filter((id) => this.scenarioData[id].selectable === true);

        if (
          !selectabelDependentDatasets.includes(this.dependentDataset as string)
        ) {
          this.dependentDataset = selectabelDependentDatasets[0];
        }

        this.updateProphetForecast();
      }
    });
  }
}
