import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
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

  public showSpinner: boolean = false;

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

  private geojsons = {
    global: {
      url: 'https://datahub.io/core/geo-countries/r/countries.geojson',
      featureidkey: 'properties.ISO_A3',
      center: { lat: 56.5, lon: 11 },
      zoom: 1.0,
    },
    germany: {
      url: 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/3_mittel.geo.json',
      featureidkey: 'properties.id',
      center: { lat: 51.3, lon: 10 },
      zoom: 3.5,
    },
  };

  createChoroplethMap(data: CountryData, selectedIdx: number) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let featureSelected = this.selections.datasets[selectedIdx].featureSelected;
    let timeSelected = this.selections.datasets[selectedIdx].timeSelected;

    if (featureSelected !== undefined && timeSelected !== undefined) {
      let first_timestamp = (Object.values(data) as any)[0][timeSelected][0];
      let all_timestamps = (Object.values(data) as any)[0][timeSelected];

      let all_keys = Object.keys(data);
      let z_min_val = 0;
      let z_max_val = 0;

      if (this.frames.length > 0) {
        this.frames = [];
      }

      for (let timestamp in all_timestamps) {
        let z_entries = [];
        for (let [key, value] of Object.entries(data)) {
          z_entries.push((value as any)[featureSelected][timestamp]);
          if (z_max_val < Number((value as any)[featureSelected][timestamp])) {
            z_max_val = (value as any)[featureSelected][timestamp];
          }
          if (z_min_val > Number((value as any)[featureSelected][timestamp])) {
            z_min_val = (value as any)[featureSelected][timestamp];
          }
        }

        let frame: Frame = {
          data: [
            {
              z: z_entries,
            },
          ],
          name: String(all_timestamps[timestamp]),
        };
        this.frames.push(frame);
      }

      let scope: string = 'global';
      let federal_states_germany = [
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

      for(let state of federal_states_germany){
        if (all_keys.includes(state)) {
          scope = 'germany';
          break;
        }
      }

      this.data = {
        data: [
          {
            type: 'choroplethmapbox',
            locations: all_keys,
            z: this.frames[0].data[0].z,
            zmin: z_min_val,
            zmax: z_max_val,
            geojson: this.geojsons[scope as keyof object]['url'],
            featureidkey: this.geojsons[scope as keyof object]['featureidkey'],
            zoom: this.geojsons[scope as keyof object]['zoom'],
            marker: { opacity: 0.7 },
          },
        ],
        layout: {
          title: 'Map Visualization for: ' + featureSelected,
          paper_bgcolor: '#232323',
          plot_bgcolor: '#232323',
          font: { color: '#f2f2f2' },
          mapbox: {
            style: 'carto-darkmatter',
            center: this.geojsons[scope as keyof object]['center'],
          },
          updatemenus: [
            {
              showactive: false,
              type: 'buttons',
              buttons: [
                {
                  args: [
                    {
                      geojson: this.geojsons['global']['url'],
                      featureidkey: this.geojsons['global']['featureidkey'],
                    },
                    {
                      mapbox: {
                        style: 'carto-darkmatter',
                        center: this.geojsons['global']['center'],
                        zoom: this.geojsons['global']['zoom'],
                      },
                    },
                  ],
                  label: 'Global',
                  method: 'update',
                },
                {
                  args: [
                    {
                      geojson: this.geojsons['germany']['url'],
                      featureidkey: this.geojsons['germany']['featureidkey'],
                    },
                    {
                      mapbox: {
                        style: 'carto-darkmatter',
                        center: this.geojsons['germany']['center'],
                        zoom: this.geojsons['germany']['zoom'],
                      },
                    },
                  ],
                  label: 'Germany',
                  method: 'update',
                },
              ],
            },
          ],
          sliders: [
            {
              currentvalue: {
                prefix: 'Year: ',
              },
              steps: this.frames.map((f) => ({
                label: f.name,
                method: 'animate',
                args: [[f.name], { frame: { duration: 0 } }],
              })),
            },
          ],
        },
      };
    }
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
                this.oldSelections?.selectedDataset
            ) {
              this.showSpinner = true;
              this.dataService
                .getData(
                  this.selections.datasets[selectedDatasetIdx],
                  '/graph/map'
                )
                .subscribe((data) => {
                  if (data.type === HttpEventType.DownloadProgress) {
                    console.log('downloading');
                  }

                  if (data.type === HttpEventType.Response) {
                    console.log('completed');
                    if (data.body) {
                      this.showSpinner = false;
                      this.createChoroplethMap(data.body as CountryData, selectedDatasetIdx);
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
  }
}