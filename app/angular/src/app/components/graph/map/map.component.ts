import { Options } from '@angular-slider/ngx-slider';
import { HttpEventType } from '@angular/common/http';
import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { GraphData, Frame, CountryData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-map',
  styleUrls: ['./map.component.css'],
  templateUrl: './map.component.html',
})
export class MapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public data: GraphData = {
    data: [],
    layout: {},
  };
  public frames: Frame[] = [];

  private selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };
  private oldSelections?: Selections;

  selectionControl = new FormGroup({
    sliderControl: new FormControl(),
    geojsonControl: new FormControl(),
  });

  options: Options = {
    showTicksValues: false,
    stepsArray: [],
    translate: (value: number): string => {
      return '';
    },
  };
  value: number = 0;

  private scope: string = 'global';
  private z_min?: number;
  private z_max?: number;
  private all_timestamps: any[] = [];
  private all_keys: string[] = [];
  private featureSelected?: string;

  geojsons_list: string[] = ['global', 'germany'];
  private geojsons = {
    global: {
      url: 'https://raw.githubusercontent.com/Sultanow/dt_society/main/app/flask/flaskr/static/geojson/countries_scaled.geojson',
      featureidkey: 'properties.ISO_A3',
      center: { lat: 56.5, lon: 11 },
      zoom: 1.0,
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

  createChoroplethMap(data: CountryData, selectedIdx: number) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    this.featureSelected =
      this.selections.datasets[selectedIdx].featureSelected;
    let timeSelected = this.selections.datasets[selectedIdx].timeSelected;

    if (this.featureSelected !== undefined && timeSelected !== undefined) {
      this.all_timestamps = (Object.values(data) as any)[0][timeSelected];

      this.all_keys = Object.keys(data);
      let z_min_val = 0;
      let z_max_val = 0;

      const newOptions: Options = Object.assign({}, this.options);
      newOptions.floor = 0;
      newOptions.ceil = this.all_timestamps.length;
      newOptions.translate = (value: number) => {
        return String(this.all_timestamps[value]);
      };
      newOptions['stepsArray'] = [];
      this.options = newOptions;
      this.value = 0;

      if (this.frames.length > 0) {
        this.frames = [];
      }

      for (let timestamp in this.all_timestamps) {
        let z_entries = [];
        for (let [key, value] of Object.entries(data)) {
          z_entries.push((value as any)[this.featureSelected][timestamp]);
          if (
            z_max_val < Number((value as any)[this.featureSelected][timestamp])
          ) {
            z_max_val = (value as any)[this.featureSelected][timestamp];
          }
          if (
            z_min_val > Number((value as any)[this.featureSelected][timestamp])
          ) {
            z_min_val = (value as any)[this.featureSelected][timestamp];
          }
        }

        let frame: Frame = {
          data: [
            {
              z: z_entries,
            },
          ],
        };
        this.frames.push(frame);
        this.options['stepsArray']!.push({
          value: Number(timestamp),
        });
      }

      this.z_min = z_min_val;
      this.z_max = z_max_val;

      for (let state of this.federal_states_germany) {
        if (this.all_keys.includes(state)) {
          this.scope = 'germany';
          break;
        }
      }

      this.createInitialData();
    }
  }

  private createInitialData() {
    this.data = {
      data: [
        {
          type: 'choroplethmapbox',
          locations: this.all_keys,
          z: this.frames[0].data[0].z,
          zmin: this.z_min,
          zmax: this.z_max,
          geojson: this.geojsons[this.scope as keyof object]['url'],
          featureidkey:
            this.geojsons[this.scope as keyof object]['featureidkey'],
          zoom: this.geojsons[this.scope as keyof object]['zoom'],
          marker: { opacity: 0.7 },
          colorscale: 'Jet',
          colorbar: {
            title: { text: this.featureSelected, side: 'top' },
            orientation: 'h',
          },
        },
      ],
      layout: {
        paper_bgcolor: '#424242',
        plot_bgcolor: '#424242',
        font: { color: '#f2f2f2' },
        mapbox: {
          style: 'carto-darkmatter',
          center: this.geojsons[this.scope as keyof object]['center'],
        },
      },
    };
  }

  private updateData(sliderValue: number) {
    let newData = [
      {
        type: 'choroplethmapbox',
        locations: this.all_keys,
        z: this.frames[sliderValue].data[0]['z' as keyof object],
        zmin: this.z_min,
        zmax: this.z_max,
        geojson: this.geojsons[this.scope as keyof object]['url'],
        featureidkey: this.geojsons[this.scope as keyof object]['featureidkey'],
        zoom: this.geojsons[this.scope as keyof object]['zoom'],
        marker: { opacity: 0.7 },
        colorscale: 'Jet',
        colorbar: {
          title: { text: this.featureSelected, side: 'top' },
          orientation: 'h',
        },
      },
    ];
    this.data.data = newData;
  }

  ngDoCheck() {
    if (
      JSON.stringify(this.selections) !== JSON.stringify(this.oldSelections)
    ) {
      if (this.selections.datasets.length > 0) {
        const datasetId = this.selections.selectedDataset;

        const selectedDatasetIdx = this.selections.datasets.findIndex(
          (dataset) => dataset.id == datasetId
        );

        if (this.selections.datasets[selectedDatasetIdx] !== undefined) {
          if (
            this.selections.datasets[selectedDatasetIdx].geoSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].reshapeSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].featureSelected !==
              undefined &&
            this.selections.datasets[selectedDatasetIdx].timeSelected !==
              undefined
          ) {
            if (
              this.selections.datasets[selectedDatasetIdx].featureSelected !==
                this.oldSelections?.datasets[selectedDatasetIdx]
                  .featureSelected ||
              this.selections.selectedDataset !==
                this.oldSelections?.selectedDataset ||
              this.selections.datasets[selectedDatasetIdx].timeSelected !==
                this.oldSelections?.datasets[selectedDatasetIdx].timeSelected
            ) {
              this.dataService
                .getData(
                  this.selections.datasets[selectedDatasetIdx],
                  '/graph/map',
                  {}
                )
                .subscribe((data) => {
                  if (data.type === HttpEventType.Response) {
                    if (data.body) {
                      this.createChoroplethMap(
                        data.body as CountryData,
                        selectedDatasetIdx
                      );
                    }
                  }
                });
            }
          }
        }
      }
      this.oldSelections = structuredClone(this.selections);
    }
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });

    this.selectionControl
      .get('sliderControl')!
      .valueChanges.subscribe((sliderValue) => {
        this.updateData(sliderValue);
      });
  }
}
