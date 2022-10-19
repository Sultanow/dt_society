import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  HttpClient,
  HttpEvent,
  HttpEventType,
  HttpRequest,
} from '@angular/common/http';
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
    return this.http.request(request);
  }

  uploadDataset(
    event: any,
    availableDatasets: AvailableDatasets,
    selectedDatasets: SelectedDatasets,
    inFocus: string | undefined
  ): void {
    const file: File = event.target.files[0];

    if (file) {
      //this.fileName = file.name;

      const formData = new FormData();

      formData.append('upload', file);

      const request = new HttpRequest('POST', this.apiUrl, formData, {
        reportProgress: true,
      });

      this.http.request(request).subscribe((event) => {
        if (event.type == HttpEventType.UploadProgress) {
          console.log('uploading');
        }
        if (event.type == HttpEventType.Response) {
          console.log('completed upload');
          this.getAvailableDatasets(
            availableDatasets,
            selectedDatasets,
            inFocus
          );
        }
      });
    }
  }

  deleteDataset(
    datasetId: string,
    availableDatasets: AvailableDatasets,
    selectedDatasets: SelectedDatasets
  ) {
    const request = new HttpRequest(
      'DELETE',
      this.apiUrl + 'datasets',
      { datasetId: datasetId },
      {
        reportProgress: true,
      }
    );

    const datasetIndex = availableDatasets.datasets
      .map((d) => d.datasetId)
      .indexOf(datasetId);

    this.http.request(request).subscribe((event) => {
      if (event.type == HttpEventType.Response && datasetIndex > -1) {
        for (const collection of [availableDatasets, selectedDatasets]) {
          collection.datasets.splice(datasetIndex);
        }
      }
    });
  }

  getAvailableDatasets(
    availableDatasets: AvailableDatasets,
    selectedDatasets: SelectedDatasets,
    inFocus: string | undefined
  ): void {
    this.http.get(this.apiUrl + 'datasets').subscribe((datasets) => {
      availableDatasets.datasets = datasets as DatasetOptions[];

      if (inFocus == undefined) {
        inFocus = availableDatasets.datasets[0].datasetId;
      }
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
