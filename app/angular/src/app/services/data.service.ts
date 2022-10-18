import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpEvent, HttpRequest } from '@angular/common/http';
import { GraphData } from '../types/GraphData';
import {
  AvailableDatasets,
  DatasetOptions,
  SelectedDatasets,
} from '../types/Datasets';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private apiUrl: string = 'http://127.0.0.1:5000/';

  constructor(private http: HttpClient) {}

  getData(columns: any, endpoint: string): Observable<HttpEvent<GraphData>> {
    const request = new HttpRequest('POST', this.apiUrl + endpoint, columns, {
      reportProgress: true,
    });
    // return this.http.post<HttpEvent<GraphData>>(
    //   this.apiUrl + endpoint,
    //   columns,
    //   {
    //     reportProgress: true,
    //   }
    return this.http.request(request);
  }

  getAvailableDatasets(
    availableDatasets: AvailableDatasets,
    selectedDatasets: SelectedDatasets,
    inFocus: string | undefined
  ): void {
    this.http.get(this.apiUrl + 'datasets').subscribe((datasets) => {
      availableDatasets.datasets = datasets as DatasetOptions[];
      inFocus = availableDatasets.datasets[0].datasetId;
      if (selectedDatasets.datasets != undefined) {
        for (const dataset of availableDatasets.datasets) {
          if (
            selectedDatasets.datasets.filter(
              (d) => d.datasetId == dataset.datasetId
            ).length == 0
          ) {
            selectedDatasets.datasets.push({
              datasetId: dataset.datasetId,
            });
          }
        }
      }
    });
  }

  getReshapedData(
    availableDatasets: AvailableDatasets,
    selectedDatasets: SelectedDatasets,
    datasetId: string,
    reshape: boolean
  ) {
    const targetIndex = availableDatasets.datasets.findIndex(
      (dataset) => dataset.datasetId == datasetId
    );

    if (
      selectedDatasets.datasets[targetIndex].geoColumn != undefined &&
      selectedDatasets.datasets[targetIndex].reshapeColumn != undefined
    ) {
      let reshapeColumn = null;

      if (reshape) {
        reshapeColumn = selectedDatasets.datasets[targetIndex].reshapeColumn;
      }

      this.http
        .post(this.apiUrl + 'datasets', {
          datasetIdx: targetIndex,
          reshapeColumn: reshapeColumn,
          geoColumn: selectedDatasets.datasets[targetIndex].geoColumn,
        })
        .subscribe((reshapedColumns) => {
          availableDatasets.datasets[targetIndex].timeOptions = (
            reshapedColumns as any
          ).timeColumns;
          availableDatasets.datasets[targetIndex].featureOptions = (
            reshapedColumns as any
          ).featureColumns;
        });
    }
  }
}
