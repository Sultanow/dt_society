import { Options } from '@angular-slider/ngx-slider';
import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { CountryData, Frame, MapForecastGraph } from 'src/app/types/GraphData';

// multivariate map based forecasting component
// (VAR, HW exponential smoothing)

@Component({
  selector: 'app-var-map',
  templateUrl: './var-map.component.html',
  styleUrls: ['./var-map.component.css'],
})
export class VarMapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: MapForecastGraph = {
    data: [[]],
    layout: {},
    config: { responsive: false },
  };

  public validDatasets: number = 0;
  public showSpinner: boolean = false;

  public frames: Frame[][] = [];

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  selectionControl = new FormGroup({
    sliderControl: new FormControl(),
    geojsonControl: new FormControl(),
  });

  options: Options = {
    showTicks: true,
    showTicksValues: false,
    stepsArray: [],
    translate: (value: number): string => {
      return '';
    },
  };
  currentSliderValue: number = 0;

  private scope: string = 'global';
  private z_min: number[] = [];
  private z_max: number[] = [];
  public timestamps: any[] = [];
  private countries: string[] = [];
  public features?: (string | undefined)[];
  public names?: (string | undefined)[][];
  public maxLags: number = 1;
  public predictionPeriods: number = 15;
  public selectedModel = 'var';

  private geojsons = {
    global: {
      url: 'https://raw.githubusercontent.com/Sultanow/dt_society/main/app/flask/flaskr/static/geojson/countries_scaled.geojson',
      featureidkey: 'properties.ISO_A3',
      center: { lat: 51.3, lon: 10 },
      zoom: 2.0,
    },
    germany: {
      url: 'https://raw.githubusercontent.com/Sultanow/dt_society/main/app/flask/flaskr/static/geojson/germany_3_mittel.geo.json',
      featureidkey: 'properties.id',
      center: { lat: 51.3, lon: 10 },
      zoom: 3.5,
    },
  };

  private federal_states_germany = [
    'DE-BB',
    'DE-BE',
    'DE-BW',
    'DE-BY',
    'DE-HB',
    'DE-HE',
    'DE-HH',
    'DE-MV',
    'DE-NI',
    'DE-NW',
    'DE-RP',
    'DE-SH',
    'DE-SL',
    'DE-SN',
    'DE-ST',
    'DE-TH',
  ];

  createChoroplethMap(data: CountryData) {
    if (this.data.data.length > 0) {
      this.data.data = [[]];
    }

    this.timestamps = data['x'] as unknown as string[];
    delete data['x'];

    this.features = this.selections.datasets
      .filter(
        (dataset) =>
          dataset.featureSelected !== undefined &&
          dataset.timeSelected !== undefined
      )
      .map((dataset) => dataset.featureSelected);

    this.names = this.selections.datasets
      .filter(
        (dataset) =>
          dataset.featureSelected !== undefined &&
          dataset.timeSelected !== undefined
      )
      .map((dataset) => [dataset.name, dataset.featureSelected]);
    this.countries = Object.keys(data);

    const newOptions: Options = Object.assign({}, this.options);
    newOptions.floor = 0;
    newOptions.ceil = this.timestamps.length;
    newOptions.translate = (value: number) => {
      return String(this.timestamps[value]);
    };
    newOptions['stepsArray'] = [];
    this.options = newOptions;
    this.currentSliderValue = 0;

    if (this.frames.length > 0) {
      this.frames = [];
    }

    // frame collections are created for each feature-dataset combination
    // to render maps seperately instead of rendering subplots
    for (let feature in this.features) {
      this.frames.push([]);
      let z_min_val = 0;
      let z_max_val = 0;
      for (let timestamp in this.timestamps) {
        let z_entries = [];
        for (let forecast of Object.values(data)) {
          z_entries.push(
            (forecast as any)[this.features[feature] as string][timestamp]
          );
          if (
            z_max_val <
            Number(
              (forecast as any)[this.features[feature] as string][timestamp]
            )
          ) {
            z_max_val = (forecast as any)[this.features[feature] as string][
              timestamp
            ];
          }
          if (
            z_min_val >
            Number(
              (forecast as any)[this.features[feature] as string][timestamp]
            )
          ) {
            z_min_val = (forecast as any)[this.features[feature] as string][
              timestamp
            ];
          }
        }

        let frame: Frame = {
          data: [
            {
              z: z_entries,
            },
          ],
        };
        this.frames[feature].push(frame);
        if (this.options['stepsArray']?.length! < this.timestamps.length) {
          this.options['stepsArray']!.push({
            value: Number(timestamp),
          });
        }
      }
      this.z_max[feature] = z_max_val;
      this.z_min[feature] = z_min_val;
    }

    this.scope = 'global';

    if (
      this.federal_states_germany.some((state) =>
        this.countries.includes(state)
      )
    ) {
      this.scope = 'germany';
    }

    this.selectionControl.get('geojsonControl')!.setValue(this.scope);

    this.showSpinner = false;
  }

  private createInitialData() {
    for (let i = 0; i < this.features?.length!; i++) {
      let choropleth: any = {
        type: 'choroplethmapbox',
        locations: this.countries,
        z: this.frames[i][0].data[0].z,
        zmin: this.z_min[i],
        zmax: this.z_max[i],
        geojson: this.geojsons[this.scope as keyof object]['url'],
        featureidkey: this.geojsons[this.scope as keyof object]['featureidkey'],
        zoom: this.geojsons[this.scope as keyof object]['zoom'],
        marker: { opacity: 0.7 },
        colorscale: 'Jet',
        colorbar: {
          orientation: 'v',
        },
      };

      if (i > 0) {
        choropleth.xaxis = 'x' + (i + 1).toString();
        choropleth.yaxis = 'y' + (i + 1).toString();
      }
      this.data.data.push([choropleth]);
    }

    this.data.layout = {
      margin: { r: 0, t: 0, l: 0, b: 0 },
      height: 250,
      paper_bgcolor: '#424242',
      plot_bgcolor: '#424242',
      font: { color: '#f2f2f2' },
      mapbox: {
        style: 'carto-darkmatter',
        center: this.geojsons[this.scope as keyof object]['center'],
        zoom: this.geojsons[this.scope as keyof object]['zoom'],
      },
      config: { responsive: false },
    };
  }

  private updateData(sliderValue: number) {
    this.currentSliderValue = sliderValue;
    this.data.data = [[]];
    for (let i = 0; i < this.features?.length!; i++) {
      this.data.data.push([
        {
          type: 'choroplethmapbox',
          locations: this.countries,
          z: this.frames[i][sliderValue].data[0]['z' as keyof object],
          zmin: this.z_min[i],
          zmax: this.z_max[i],
          geojson: this.geojsons[this.scope as keyof object]['url'],
          featureidkey:
            this.geojsons[this.scope as keyof object]['featureidkey'],
          marker: { opacity: 0.7 },
          colorscale: 'Jet',
          colorbar: {
            orientation: 'v',
          },
        },
      ]);
    }
  }

  updateForecastData() {
    const filteredSelections = this.selections.datasets.filter(
      (dataset) =>
        dataset.featureSelected !== undefined &&
        dataset.timeSelected !== undefined
    );

    if (filteredSelections.length > 1) {
      this.showSpinner = true;
      this.dataService
        .getData(filteredSelections, '/forecast/map/' + this.selectedModel, {
          periods: 15,
          maxLags: this.maxLags,
        })
        .subscribe((data) => {
          if (data.type === HttpEventType.Response) {
            if (data.body) {
              this.createChoroplethMap(data.body as CountryData);
            }
          }
        });
    }
  }
  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      this.validDatasets = 0;
      if (this.selections.datasets.length > 0) {
        this.selections.datasets.forEach((dataset) => {
          if (
            dataset.featureSelected !== undefined &&
            dataset.timeSelected !== undefined
          ) {
            this.validDatasets++;
          }
        });
      }
      this.updateForecastData();
    });

    this.selectionControl
      .get('sliderControl')!
      .valueChanges.subscribe((sliderValue) => {
        this.updateData(sliderValue);
      });

    this.selectionControl
      .get('geojsonControl')!
      .valueChanges.subscribe((value) => {
        this.scope = String(value);
        this.createInitialData();
      });
  }
}
