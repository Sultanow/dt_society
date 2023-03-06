import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import {
  ColumnValues,
  Plot,
  Scenario,
  ScenarioData,
} from 'src/app/types/GraphData';
import { Options } from '@angular-slider/ngx-slider';
import { faCaretDown } from '@fortawesome/free-solid-svg-icons';

// multivariate graph based forecasting component
// (VAR, HW exponential smoothing)

@Component({
  selector: 'app-vectorautoregression',
  templateUrl: './vectorautoregression.component.html',
  styleUrls: ['./vectorautoregression.component.css'],
})
export class VectorautoregressionComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  settingsIcon = faCaretDown;

  // Binded properties
  public countries: string[] = [];
  public predictionPeriods: number = 0;
  public alphaParameter: number = 0.49;
  public frequency: string = 'Yearly';
  public selectedModel: string = 'var';
  public showSpinner: boolean = false;
  public validDatasets: number = 0;
  public validData: boolean = false;
  public scenarios: ScenarioData = {};

  public data: Plot = {
    data: [],
    layout: {
      showlegend: false,
      legend: { title: { text: '' }, valign: 'top' },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      title: '',
    },
    config: { responsive: true },
  };

  options: Options = {
    floor: 0,
    ceil: 0,
    showTicks: true,
  };

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

  createVarForecast(data: ColumnValues): void {
    // Renders plot from received data
    if (this.data.data.length > 0) {
      this.data.data = [];
    }
    console.log(data);

    if (data['future'] !== undefined) {
      this.updateSlider(data['future'] as string[]);
      delete data['future'];
    } else {
      this.updateSlider();
    }

    let plotCount = Object.keys(data).length - 1;
    let colCount = plotCount === 1 ? 1 : 2;
    let rowCount = Math.ceil(plotCount / 2);
    this.data.layout.grid = {
      rows: rowCount,
      columns: colCount,
      pattern: 'independent',
    };
    this.data.layout.height = rowCount * 350;

    const colors = [
      'mediumpurple',
      'mediumspringgreen',
      'hotpink',
      'mediumblue',
      'goldenrod',
      '#1f77b4',
      '#ff7f0e',
      '#2ca02c',
      '#d62728',
      '#9467bd',
      '#8c564b',
      '#e377c2',
      '#7f7f7f',
      '#bcbd22',
      '#17becf',
    ];

    const breakString = (str: string, maxChars: number): string => {
      if (str.length > maxChars && str.includes(' ')) {
        let index = str.lastIndexOf(' ', maxChars);
        if (index === -1) index = str.indexOf(' ', maxChars + 1);
        return (
          str.substring(0, index) +
          '</br>' +
          breakString(str.substring(index + 1), maxChars)
        );
      } else {
        return str;
      }
    };

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
        trace_solid.name = '</br>' + breakString(key, 20);

        trace_dashed.y = value.slice(-this.predictionPeriods - 1);
        trace_dashed.x = data['x'].slice(-this.predictionPeriods - 1);
        trace_dashed.name = '</br>' + breakString(key + ' Prediction', 20);
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
          this.scenarios[dataset.id as string].active === true
      );
      if (
        filteredSelections.length > 1 ||
        (filteredSelections.length === 1 &&
          filteredSelections[0].varFeaturesSelected !== undefined &&
          filteredSelections[0].varFeaturesSelected.length > 1)
      ) {
        this.checkValidData();
        this.showSpinner = true;
        this.dataService
          .getData(
            filteredSelections,
            '/forecast/multivariate/' + this.selectedModel,
            {
              country: this.selections.selectedCountry,
              periods: this.predictionPeriods,
              maxLags: this.alphaParameter,
              frequency: this.frequency,
            }
          )
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.createVarForecast(event.body as ColumnValues);
                this.showSpinner = false;
              }
            }
          });
      } else {
        this.validData = false;
      }
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((updatedSelections) => {
      this.selections = updatedSelections;
      this.validData = false;
      this.validDatasets = 0;
      this.scenarios = {};

      if (this.selections.datasets.length > 0) {
        this.selections.datasets.forEach((dataset) => {
          dataset.varFeaturesSelected = [dataset.featureSelected!];
          if (
            dataset.countryOptions?.includes(this.selections.selectedCountry!)
          ) {
            this.validDatasets++;
          }

          this.scenarios[dataset.id!] = {} as Scenario;

          this.scenarios[dataset.id as string].selectable =
            dataset.countryOptions?.includes(
              this.selections.selectedCountry as string
            ) as boolean;
          this.scenarios[dataset.id as string].active =
            dataset.countryOptions?.includes(
              this.selections.selectedCountry as string
            ) as boolean;
        });

        this.checkValidData();
      }
      this.updateVarForecast();
    });
  }

  private checkValidData() {
    if (
      this.validDatasets > 1 ||
      this.selections.datasets.some(
        (dataset) =>
          dataset.varFeaturesSelected !== undefined &&
          dataset.varFeaturesSelected.length > 1
      )
    ) {
      this.validData = true;
    }
  }
}
