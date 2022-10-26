import { HttpEventType } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';
import { CountryData, GraphData, MapPlot } from 'src/app/types/GraphData';

interface Frame {
  data: {};
  layout: {};
  name: string;
}

@Component({
  selector: 'app-map',
  styleUrls: ['./map.component.css'],
  templateUrl: './map.component.html',
})
export class MapComponent implements OnInit {
  constructor(private dataService: DataService) {}

  public frames: Frame[] = [];

  public data: GraphData = {
    data: [],
    layout: {},
  };

  public selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  showSpinner: boolean = false;

  private oldSelections?: Selections;

  createChoroplethMap(data: {}, selectedIdx: number) {
    if (this.data.data.length > 0) {
      this.data.data = [];
    }

    let first_year = (Object.values(data) as any)[0]['Time'][0];
    let all_years = (Object.values(data) as any)[0]['Time'];
    let all_keys = Object.keys(data);

    let feature = this.selections.datasets[selectedIdx].featureSelected;
    let max_val = 0;
    let initial_z = [];

    if (feature !== undefined) {
      for (let year in all_years) {
        let z_entries = [];
        for (let [key, value] of Object.entries(data)) {
          z_entries.push((value as any)[feature][year]);
          if (String(year) === '0') {
            initial_z.push((value as any)[feature][0]);
          }
          if (max_val < Number((value as any)[feature][year])) {
            max_val = (value as any)[feature][year];
          }
        }
        let frame: Frame = {
          data: [
            {
              z: z_entries,
              locations: all_keys,
            },
          ],
          layout: {
            title: 'Choropleth Plot',
            paper_bgcolor: '#232323',
            plot_bgcolor: '#232323',
            mapbox: {
              style: 'carto-darkmatter',
            },
          },
          name: String(all_years[year]),
        };
        this.frames.push(frame);
      }

      this.data = {
        data: [
          {
            type: 'choroplethmapbox',
            locations: all_keys,
            z: initial_z,
            zmin: 0,
            zmax: max_val,
            geojson:
              'https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson',
            featureidkey: 'properties.ISO3',
            marker: { opacity: 0.7 },
          },
        ],
        layout: {
          title: 'Choropleth Plot',
          paper_bgcolor: '#232323',
          plot_bgcolor: '#232323',
          font: { color: '#f2f2f2' },
          mapbox: {
            style: 'carto-darkmatter',
            center: { lat: 53, lon: 9 },
          },
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
                      this.createChoroplethMap(data.body, selectedDatasetIdx);
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
