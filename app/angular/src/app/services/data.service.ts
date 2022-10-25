import { Injectable, Input } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import {
  HttpClient,
  HttpEvent,
  HttpEventType,
  HttpRequest,
} from '@angular/common/http';
import {
  ColumnValues,
  CorrelationMatrix,
  CountryData,
  GraphData,
  MapPlot,
  Plot,
} from '../types/GraphData';
import { Dataset, Selections } from '../types/Datasets';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private apiUrl: string = 'http://127.0.0.1:5000/';

  private selections: BehaviorSubject<Selections> = new BehaviorSubject(<
    Selections
  >{
    datasets: [],
    targetDatasetIdx: undefined,
  });
  currentSelections = this.selections.asObservable();

  constructor(private http: HttpClient) {}

  updateDatasetsSelection(newDataSel: Selections) {
    this.selections.next(newDataSel);
  }

  getData(
    columns: any,
    endpoint: string
  ): Observable<HttpEvent<CorrelationMatrix | CountryData | ColumnValues[]>> {
    const request = new HttpRequest('POST', this.apiUrl + endpoint, columns, {
      reportProgress: true,
    });
    return this.http.request(request);
  }

  uploadDataset(event: any, selections: Selections): void {
    const file: File = event.target.files[0];

    if (file) {
      const formData = new FormData();

      formData.append('upload', file);

      const request = new HttpRequest(
        'POST',
        this.apiUrl + 'data/upload',
        formData,
        {
          reportProgress: true,
        }
      );

      this.http.request(request).subscribe((event) => {
        if (event.type == HttpEventType.UploadProgress) {
          console.log('uploading');
        }
        if (event.type == HttpEventType.Response) {
          console.log('completed upload');
          this.getAvailableDatasets(selections);
        }
      });
    }
  }

  deleteDataset(datasetId: string | undefined, selections: Selections) {
    const request = new HttpRequest(
      'DELETE',
      this.apiUrl + 'data/remove',
      { datasetId: datasetId },
      {
        reportProgress: true,
      }
    );

    const selectedDatasetIndex = selections.datasets
      .map((d) => d.id)
      .indexOf(datasetId);

    this.http.request(request).subscribe((event) => {
      if (event.type == HttpEventType.Response && selectedDatasetIndex > -1) {
        selections.datasets.splice(selectedDatasetIndex);
      }
    });
  }

  getAvailableDatasets(selections: Selections): void {
    this.http.get(this.apiUrl + 'data').subscribe((datasets) => {
      let updatedDatasets = datasets as Dataset[];

      if (selections.datasets != undefined) {
        for (const dataset of updatedDatasets) {
          if (
            selections.datasets.filter((d) => d.id == dataset.id).length == 0
          ) {
            selections.datasets.push(dataset);
          }
        }
        if (selections.selectedDataset == undefined) {
          selections.selectedDataset = selections.datasets[0].id;
        }
      }
    });
  }

  getReshapedData(
    selections: Selections,
    datasetId: string | undefined,
    reshape: boolean
  ) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );

    if (
      selections.datasets[targetDatasetIdx].geoSelected != undefined &&
      selections.datasets[targetDatasetIdx].reshapeSelected != undefined
    ) {
      let reshapeColumn = null;

      if (reshape) {
        reshapeColumn = selections.datasets[targetDatasetIdx].reshapeSelected;
      }

      this.http
        .post(this.apiUrl + 'data/reshape', {
          datasetIdx: selections.datasets[targetDatasetIdx].id,
          reshapeColumn: reshapeColumn,
          geoColumn: selections.datasets[targetDatasetIdx].geoSelected,
        })
        .subscribe((reshapedColumns) => {
          selections.datasets[targetDatasetIdx].timeOptions = (
            reshapedColumns as Dataset
          ).timeOptions;
          selections.datasets[targetDatasetIdx].featureOptions = (
            reshapedColumns as Dataset
          ).featureOptions;
        });
    }
  }
}
