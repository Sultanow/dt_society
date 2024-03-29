import { Component, OnInit } from '@angular/core';
import { Options } from '@angular-slider/ngx-slider';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { HttpEventType } from '@angular/common/http';
import { FormControl, FormGroup, UntypedFormControl } from '@angular/forms';
import { CountryData } from 'src/app/types/GraphData';
import { ReplaySubject } from 'rxjs';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.css'],
})
export class StatisticsComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public showSpinner: boolean = false;

  data: CountryData = {};

  geodata: boolean = true;

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };
  private oldSelections?: Selections;

  public dataAvailable: boolean = false;

  selectedCountry: string = '';
  oldSelectedCountry?: string;

  value: number = 0;
  highValue: number = 0;
  options: Options = {
    floor: 0,
    ceil: 0,
    showTicks: true,
  };

  selectionControl = new FormGroup({
    selectedYearControl: new FormControl(),
    selectedCountryControl: new FormControl(),
    countryFilterControl: new UntypedFormControl(),
  });

  public filteredCountries: ReplaySubject<(undefined | string)[]> =
    new ReplaySubject<(undefined | string)[]>(1);

  timestamps: (undefined | string[] | string | number)[] = [];
  countries: (undefined | string)[] = [];

  min: String = '';
  min_key: String = '';
  max: String = '';
  max_key: String = '';
  mean: String = '';

  growthrate: String = '';
  growthrate_per_time: String = '';

  updateData(newdata: CountryData) {
    const selectedDatasetIdx = this.selections.datasets.findIndex(
      (dataset) => dataset.id === this.selections.selectedDataset
    );

    if (
      Object.keys(newdata).includes(
        this.selections.datasets[selectedDatasetIdx].featureSelected!
      )
    ) {
      this.updateNoGeoData(newdata, selectedDatasetIdx);
    } else {
      this.updateGeoData(newdata);
    }
  }

  private updateGeoData(newdata: CountryData) {
    this.geodata = true;
    this.data = newdata;
    this.countries = [];

    const selectedDatasetIdx = this.selections.datasets.findIndex(
      (dataset) => dataset.id == this.selections.selectedDataset
    );

    let timearray =
      Object.entries(newdata)[0][1][
        this.selections.datasets[selectedDatasetIdx].timeSelected!
      ];
    this.timestamps = timearray.map(String);
    for (const [key, value] of Object.entries(newdata)) {
      this.countries = [...this.countries, key];
    }

    this.filteredCountries.next(this.countries.slice());

    this.updateSlider(timearray);
    this.resetStatistics();

    this.dataAvailable = true;
  }

  private updateNoGeoData(newdata: CountryData, selectedDatasetIdx: number) {
    this.geodata = false;
    this.data = newdata;
    let timearray = newdata[
      this.selections.datasets[selectedDatasetIdx].timeSelected!
    ] as unknown as string[];
    this.updateSlider(timearray);

    let dataarray = newdata[
      this.selections.datasets[selectedDatasetIdx].featureSelected!
    ] as unknown as [];

    let min = null;
    let min_key: string = '';
    let max = null;
    let max_key: string = '';
    let sum = 0;
    for (const [i, value] of dataarray.entries()) {
      let current_val = value as number;
      if (min === null || min > current_val) {
        min = current_val;
        min_key = timearray[i];
      }
      if (max === null || max < current_val) {
        max = current_val;
        max_key = timearray[i];
      }
      sum = sum + current_val;
    }
    this.mean = (sum / dataarray.length).toFixed(3).toString();
    this.min = min!.toFixed(3).toString();
    this.min_key = min_key;
    this.max = max!.toFixed(3).toString();
    this.max_key = max_key;

    this.dataAvailable = true;
  }

  updateGrowth() {
    const selectedDatasetIdx = this.selections.datasets.findIndex(
      (dataset) => dataset.id == this.selections.selectedDataset
    );

    this.selectedCountry = this.selectionControl
      .get('selectedCountryControl')!
      .getRawValue();

    let feature = this.selections.datasets[selectedDatasetIdx].featureSelected!;
    let firstValue: number;
    let secondValue: number;
    if (this.geodata) {
      firstValue = this.data[this.selectedCountry][feature][
        this.value
      ] as number;
      secondValue = this.data[this.selectedCountry][feature][
        this.highValue
      ] as number;
    } else {
      firstValue = (this.data[feature] as unknown as [])[this.value] as number;
      secondValue = (this.data[feature] as unknown as [])[
        this.highValue
      ] as number;
    }

    let tempGrowthrate = (secondValue - firstValue) / firstValue;
    this.growthrate = (tempGrowthrate * 100).toFixed(3) + '%';
    this.growthrate_per_time =
      ((tempGrowthrate * 100) / (this.highValue - this.value)).toFixed(3) + '%';
  }

  updateStats(timestamp: string) {
    const selectedDatasetIdx = this.selections.datasets.findIndex(
      (dataset) => dataset.id == this.selections.selectedDataset
    );
    let timestamp_index = this.timestamps.indexOf(timestamp);
    let feature = this.selections.datasets[selectedDatasetIdx].featureSelected!;

    let min = null;
    let min_key: string = '';
    let max = null;
    let max_key: string = '';
    let sum = 0;
    for (let [key, value] of Object.entries(this.data)) {
      let current_val = value[feature][timestamp_index] as number;
      if (min === null || min > current_val) {
        min = current_val;
        min_key = key;
      }
      if (max === null || max < current_val) {
        max = current_val;
        max_key = key;
      }
      sum += current_val;
    }

    this.mean = (sum / Object.entries(this.data).length).toFixed(3).toString();
    this.min = min!.toFixed(3).toString();
    this.min_key = min_key;
    this.max = max!.toFixed(3).toString();
    this.max_key = max_key;
  }

  private updateSlider(timearray: string[] | number[]) {
    const newOptions: Options = Object.assign({}, this.options);
    newOptions.floor = 0 as number;
    newOptions.ceil = (timearray.length - 1) as number;
    newOptions.translate = (value: number) => {
      return String(timearray[value]);
    };
    timearray.length > 50
      ? (newOptions.showTicks = false)
      : (newOptions.showTicks = true);
    this.options = newOptions;
    this.value = newOptions.floor;
    this.highValue = newOptions.ceil;
  }

  private resetStatistics() {
    this.selectionControl
      .get('selectedCountryControl')!
      .setValue(this.countries[0]);
    this.selectionControl
      .get('selectedYearControl')!
      .setValue(this.timestamps[0]);
  }

  private getData() {
    if (this.selections.datasets.length > 0) {
      const datasetId = this.selections.selectedDataset;

      const selectedDatasetIdx = this.selections.datasets.findIndex(
        (dataset) => dataset.id == datasetId
      );

      let selectedDataset = this.selections.datasets[selectedDatasetIdx];

      if (selectedDataset !== undefined) {
        if (
          selectedDataset.featureSelected !== undefined &&
          selectedDataset.timeSelected !== undefined
        ) {
          if (
            selectedDataset.featureSelected !==
              this.oldSelections?.datasets[selectedDatasetIdx]
                .featureSelected ||
            this.selections.selectedDataset !==
              this.oldSelections?.selectedDataset ||
            selectedDataset.timeSelected !==
              this.oldSelections?.datasets[selectedDatasetIdx].timeSelected
          ) {
            this.showSpinner = true;
            this.dataService
              .getData(selectedDataset, '/graph/statistics', {})
              .subscribe((res) => {
                if (res.type === HttpEventType.Response) {
                  if (res.body) {
                    this.updateData(res.body as CountryData);
                    this.showSpinner = false;
                  }
                }
              });
            this.oldSelections = structuredClone(this.selections);
          }
        } else {
          this.dataAvailable = false;
        }
      }
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      this.getData();
    });

    this.selectionControl
      .get('countryFilterControl')!
      .valueChanges.subscribe(() => {
        this.filterCountries();
      });

    this.selectionControl
      .get('selectedYearControl')!
      .valueChanges.subscribe((selectedYear) => {
        if (this.selectionControl.get('selectedYearControl')!.value !== null) {
          this.updateStats(selectedYear.toString());
        }
      });

    this.selectionControl
      .get('selectedCountryControl')!
      .valueChanges.subscribe(() => {
        if (
          this.selectionControl.get('selectedCountryControl')!.value !== null
        ) {
          this.updateGrowth();
        }
      });
  }

  protected filterCountries() {
    if (!this.countries) {
      return;
    }
    let search = this.selectionControl.get('countryFilterControl')!.value;
    if (!search) {
      this.filteredCountries.next(this.countries.slice());
      return;
    } else {
      search = search.toLowerCase();
    }

    this.filteredCountries.next(
      this.countries.filter((country) =>
        country!.toLowerCase().includes(search)
      )
    );
  }
}
