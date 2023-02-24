import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import {
  ColumnValues,
  Plot,
  Scenario,
  ScenarioData,
} from 'src/app/types/GraphData';

interface CheckBoxToggle {
  [datasetId: string]: boolean;
}

@Component({
  selector: 'app-correlation',
  styleUrls: ['./correlation.component.css'],
  templateUrl: './correlation.component.html',
})
export class CorrelationComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public showSpinner: boolean = false;

  public data: Plot = {
    data: [],
    layout: {
      legend: { title: { text: '' }, groupclick: 'toggleitem' },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      margin: { t: 15, b: 50, l: 35 },
    },
    config: { responsive: true },
  };

  public matchingFrequencies?: boolean;
  public activeDatasets: ScenarioData = {};

  selectionControl = new FormGroup({
    selectedCountryControl: new FormControl(),
  });

  countries: (undefined | string[] | string)[] = [];

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  createCorrelationLines(data: ColumnValues[]) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    if (Object.keys(data.slice(-1)[0]).includes('matchingFrequencies')) {
      const matchingFrequencyFlag = data.pop();

      this.matchingFrequencies = matchingFrequencyFlag![
        'matchingFrequencies'
      ] as unknown as boolean;
    }

    data = data.filter((set) =>
      Object.values(set).every((val) => (val as []).length > 0)
    );

    this.data.layout.grid = {
      rows: Math.ceil(data.length / 2),
      columns: data.length === 1 ? 1 : 2,
      pattern: 'independent',
    };

    this.data.layout.height = Math.ceil(data.length / 2) * 400;

    let group = 0;
    for (let i = 0; i < data.length; i++) {
      let setId = data[i]['datasetid'].toString();

      for (const [key, value] of Object.entries(data[i])) {
        let dataset = this.selections.datasets.filter(
          (dataset) => dataset.id == setId
        )[0];
        if (
          key === 'timestamps' ||
          key === 'datasetid' ||
          key == dataset.timeSelected
        ) {
          continue;
        }

        let trace: any = {
          type: 'scatter',
          mode: 'lines',
          legendgroup: 'df' + group.toString(),
          legendgrouptitle: { text: dataset.name },
        };

        if (key !== dataset.timeSelected) {
          trace.x = data[i][dataset.timeSelected!];

          trace.y = value;
          trace.name = key;
          if (group > 0) {
            trace.xaxis = 'x' + (group + 1).toString();
            trace.yaxis = 'y' + (group + 1).toString();

            this.data.layout['xaxis' + (group + 1).toString()] = {
              gridcolor: 'rgba(80, 103, 132, 0.3)',
              title: dataset.timeSelected,
              range: data[i]['timestamps'] as number[],
            };
            this.data.layout['yaxis' + (group + 1).toString()] = {
              gridcolor: 'rgba(80, 103, 132, 0.3)',
              title: '',
            };
          } else {
            this.data.layout.xaxis = {
              gridcolor: 'rgba(80, 103, 132, 0.3)',
              title: dataset.timeSelected,
              range: data[i]['timestamps'] as number[],
            };
          }
          this.data.data.push(trace);
        }
      }
      group++;
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      this.activeDatasets = {};
      for (const dataset of this.selections.datasets) {
        this.activeDatasets[dataset.id!] = {} as Scenario;
        this.activeDatasets[dataset.id as string].active =
          dataset.countryOptions?.includes(
            this.selections.selectedCountry as string
          ) as boolean;

        this.activeDatasets[dataset.id as string].selectable =
          dataset.countryOptions?.includes(
            this.selections.selectedCountry as string
          ) as boolean;
      }

      this.updateCorrelationPlot();
    });
  }

  public updateCorrelationPlot() {
    if (this.selections.datasets.length > 0) {
      this.showSpinner = true;
      const filteredSelections = this.selections.datasets.filter(
        (dataset) =>
          dataset.featureSelected !== undefined &&
          dataset.timeSelected !== undefined &&
          this.activeDatasets[dataset.id as string].active === true
      );
      this.dataService
        .getData(filteredSelections, '/graph/corr', {
          country: this.selections.selectedCountry,
        })
        .subscribe((event) => {
          if (event.type === HttpEventType.Response) {
            if (event.body) {
              this.createCorrelationLines(event.body as ColumnValues[]);
              this.showSpinner = false;
            }
          }
        });
    }
  }
}
