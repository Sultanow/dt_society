import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { Plot } from 'src/app/types/GraphData';

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

  updateScenarios() {
    this.scenarioIndeces = new Array(this.predictionPeriods)
      .fill(null)
      .map((_, i) => i + 1);

    this.scenarioValues = new Array(this.predictionPeriods).fill(null);

    console.log(this.scenarioValues);
  }

  createProphetForecast() {}

  updateProphetForecast() {
    console.log('clicked');
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
            scenarios: this.scenarioValues,
          })
          .subscribe((event) => {
            if (event.type === HttpEventType.Response) {
              if (event.body) {
                this.createProphetForecast();
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
      console.log(this.scenarioValues);
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
