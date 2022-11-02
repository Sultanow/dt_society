import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { Plot, ProphetForecast, Scenarios } from 'src/app/types/GraphData';

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
      paper_bgcolor: '#232323',
      plot_bgcolor: '#232323',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      title: '',
    },
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  selectedScenarios = new FormControl('');

  private oldSelections?: Selections;

  public countries: string[] = [];

  public selectedCountry?: string;

  public scenarioIndeces: number[] = [];
  public scenarioValues: string[] = [];

  public predictionPeriods: number = 0;

  public frequency: string = 'Yearly';

  public scenarios: Scenarios = {};

  updateScenarios() {
    this.scenarioIndeces = new Array(this.predictionPeriods)
      .fill(null)
      .map((_, i) => i);

    //this.scenarioValues = new Array(this.predictionPeriods).fill(null);

    for (const dataset of this.selections.datasets) {
      if (
        dataset.id !== undefined &&
        dataset.id !== this.selections.selectedDataset
      ) {
        this.scenarios[dataset.id] = new Array(this.predictionPeriods).fill(
          null
        );
      }
    }

    console.log(this.scenarios);
  }

  createProphetForecast(data: ProphetForecast) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    this.data.layout.grid = {
      rows: 1,
      columns: this.selections.datasets.length,
      pattern: 'independent',
    };

    let forecastHistory: any = {
      type: 'scatter',
      mode: 'lines',
      y: data['merge'][this.selections.datasets[0].featureSelected || ''],
      x: data['merge']['x'],
      name: this.selections.datasets[0].featureSelected,
      line: { color: 'mediumpurple' },
    };

    const uncertaintyUpper = data['forecast']['yhat_upper'].map(
      (x, i) => x - data['forecast']['yhat'][i]
    );

    console.log(uncertaintyUpper);

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
      name: this.selections.datasets[0].featureSelected + ' (prediction)',
    };

    const fillerX = [data['merge']['x'].slice(-1)[0], data['forecast']['x'][0]];

    console.log(fillerX);

    let filler: any = {
      type: 'scatter',
      mode: 'lines',
      line: { dash: 'dash', color: 'mediumpurple' },
      x: fillerX,
      y: [
        data['merge'][this.selections.datasets[0].featureSelected || ''].slice(
          -1
        )[0],
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
      title: this.selections.datasets[0].featureSelected,
    };
    // forecast plot
    this.data.data.push(forecastHistory);
    this.data.data.push(forecastData);
    this.data.data.push(filler);

    // scenario plots

    const colors = ['mediumspringgreen', 'hotpink', 'mediumblue', 'goldenrod'];

    var indexFeatures = 1;

    for (const [key, value] of Object.entries(data['future'])) {
      if (key === 'x') {
        continue;
      }
      let trace_solid: any = {
        type: 'scatter',
        mode: 'lines',
        line: { color: colors[indexFeatures - 1] },
        name: key,
      };

      let trace_dashed: any = {
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'dash', color: colors[indexFeatures - 1] },
        name: key + ' (scenario)',
      };

      trace_solid.x = data['merge']['x'];
      trace_solid.y = data['merge'][key];

      trace_dashed.x = data['future']['x'];
      trace_dashed.y = data['future'][key];

      trace_solid.xaxis = 'x' + (indexFeatures + 1).toString();
      trace_solid.yaxis = 'y' + (indexFeatures + 1).toString();
      trace_dashed.xaxis = 'x' + (indexFeatures + 1).toString();
      trace_dashed.yaxis = 'y' + (indexFeatures + 1).toString();

      this.data.layout['xaxis' + (indexFeatures + 1).toString()] = {
        gridcolor: 'rgba(80, 103, 132, 0.3)',
        title: 'Time',
      };
      this.data.layout['yaxis' + (indexFeatures + 1).toString()] = {
        gridcolor: 'rgba(80, 103, 132, 0.3)',
        title: key,
      };

      indexFeatures++;
      this.data.data.push(trace_solid);
      this.data.data.push(trace_dashed);
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
        this.dataService
          .getData(this.selections.datasets, '/forecast/prophet', {
            country: this.selectedCountry,
            periods: this.predictionPeriods,
            frequency: this.frequency,
            scenarios: this.scenarios,
          })
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.createProphetForecast(event.body as ProphetForecast);
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

      var countries: string[] | undefined = [] || undefined;

      if (this.selections.datasets.length > 0) {
        for (const data of this.selections.datasets) {
          countries = [...countries, ...(data.countryOptions || [])];
        }

        this.countries = [...new Set(countries)];
      }
    });

    this.selectedScenarios.valueChanges.subscribe((scenarios) => {
      console.log(scenarios);
    });
  }
}
