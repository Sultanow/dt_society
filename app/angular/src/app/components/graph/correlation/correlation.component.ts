import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { ColumnValues, Plot } from 'src/app/types/GraphData';

@Component({
  selector: 'app-correlation',
  styleUrls: ['./correlation.component.css'],
  templateUrl: './correlation.component.html',
})
export class CorrelationComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: Plot = {
    data: [],
    layout: {
      legend: { title: { text: '' }, groupclick: 'toggleitem' },
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      xaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      yaxis: { gridcolor: 'rgba(80, 103, 132, 0.3)', title: '' },
      font: { color: '#f2f2f2' },
      margin: { t: 30, r: 100 },
    },
    config: {responsive: true}
  };

  selectionControl = new FormGroup({
    selectedCountryControl: new FormControl(),
  });

  countries: (undefined | string[] | string)[] = [];

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  private oldSelections?: Selections;
  public selectedCountry?: string;

  createCorrelationLines(data: ColumnValues[]) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let validDataframes: boolean[] = [];
    for (let i = 0; i < data.length; i++) {
      let timeOption = this.selections.datasets[i].timeSelected;
      data[i][timeOption!].length > 0
        ? (validDataframes[i] = true)
        : (validDataframes[i] = false);
    }

    this.data.layout.grid = {
      rows: 1,
      columns: validDataframes.filter(Boolean).length,
      pattern: 'independent',
    };

    let group = 0;
    for (let i = 0; i < data.length; i++) {
      const timeSelection = this.selections.datasets[i].timeSelected;
      if (validDataframes[i]) {
        for (const [key, value] of Object.entries(data[i])) {
          if (key === 'timestamps') {
            continue;
          }
          let trace: any = {
            type: 'scatter',
            mode: 'lines',
            legendgroup: 'df' + group.toString(),
            legendgrouptitle: { text: this.selections.datasets[i].id },
          };

          if (key !== timeSelection) {
            if (timeSelection !== undefined) {
              trace.x = data[i][timeSelection];
            }

            trace.y = value;
            trace.name = key;
            if (group > 0) {
              trace.xaxis = 'x' + (group + 1).toString();
              trace.yaxis = 'y' + (group + 1).toString();

              this.data.layout['xaxis' + (group + 1).toString()] = {
                gridcolor: 'rgba(80, 103, 132, 0.3)',
                title: timeSelection,
                range: data[i]['timestamps'] as number[],
              };
              this.data.layout['yaxis' + (group + 1).toString()] = {
                gridcolor: 'rgba(80, 103, 132, 0.3)',
                title: '',
              };
            } else {
              this.data.layout.xaxis = {
                gridcolor: 'rgba(80, 103, 132, 0.3)',
                title: timeSelection,
                range: data[i]['timestamps'] as number[],
              };
            }
            this.data.data.push(trace);
          }
        }
        group++;
      }
    }
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      this.updateCountries();
    }
    this.oldSelections = structuredClone(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      this.updateCountries();
    });
    this.selectionControl
      .get('selectedCountryControl')!
      .valueChanges.subscribe((selectedCountry) => {
        this.selectedCountry = selectedCountry;
        this.updateCorrelationPlot();
      });
  }

  private updateCountries() {
    var countries: string[] | undefined = [] || undefined;
    for (const dataset of this.selections.datasets) {
      if (dataset.featureOptions !== undefined) {
        countries = [...countries, ...(dataset.countryOptions || [])];
      }
    }
    this.countries = [...new Set(countries)];
    this.selectionControl.get('selectedCountryControl')!.setValue('');
  }

  private updateCorrelationPlot() {
    if (
      this.selections.datasets.length > 0 &&
      this.countries.includes(this.selectedCountry)
    ) {
      if (
        !this.selections.datasets.some(
          (dataset) =>
            dataset.geoSelected === undefined ||
            dataset.timeSelected === undefined
        )
      ) {
        this.dataService
          .getData(this.selections.datasets, '/graph/corr', {
            country: this.selectedCountry,
          })
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.createCorrelationLines(event.body as ColumnValues[]);
              }
            }
          });
      }
    }
  }
}
