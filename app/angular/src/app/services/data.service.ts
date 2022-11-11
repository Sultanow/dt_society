import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, throwError, catchError } from 'rxjs';
import {
  HttpClient,
  HttpEvent,
  HttpEventType,
  HttpRequest,
  HttpErrorResponse,
} from '@angular/common/http';
import {
  ColumnValues,
  CorrelationMatrix,
  CountryData,
  GraphControls,
} from '../types/GraphData';
import { Dataset, Options, Selections } from '../types/Datasets';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  private apiUrl: string = 'http://127.0.0.1:5000/';

  private selections: BehaviorSubject<Selections> =
    new BehaviorSubject<Selections>({
      datasets: [],
    });
  currentSelections = this.selections.asObservable();

  constructor(private http: HttpClient, private _snackBar: MatSnackBar) {}

  updateDatasetsSelection(newDataSel: Selections) {
    this.selections.next(newDataSel);
  }

  private handleError(cause: string) {
    return (error: HttpErrorResponse) => {
      if (error.status == 0) {
        console.error('An error occured:', error.error);
      } else {
        console.error(
          `Backend returned code ${error.status}, body was: `,
          error.error
        );
      }

      this._snackBar.open(
        'Something went wrong while trying to ' + cause,
        'Close',
        {
          duration: 4000,
          horizontalPosition: 'end',
          verticalPosition: 'bottom',
        }
      );

      return throwError(
        () => new Error('Something bad happened; please try again later.')
      );
    };
  }

  getDemoData(selections: Selections) {
    this.http
      .get(this.apiUrl + 'data/demo')
      .pipe(catchError(this.handleError('Demo mode')))
      .subscribe((value) => {
        this._snackBar.open('Successfully downloaded demo data', 'Close', {
          duration: 4000,
          horizontalPosition: 'end',
          verticalPosition: 'bottom',
        });
        this.getAvailableDatasets(selections);
        this.updateDatasetsSelection(selections);
      });
  }

  getData(
    columns: any,
    endpoint: string,
    {
      country,
      features,
      frequency,
      periods,
      maxLags,
      scenarios,
      dependentDataset,
    }: GraphControls
  ): Observable<
    HttpEvent<CorrelationMatrix | CountryData | ColumnValues[] | unknown>
  > {
    let body = {};

    body = {
      datasets: columns,
      features: features,
      country: country,
      frequency: frequency,
      periods: periods,
      maxLags: maxLags,
      scenarios: scenarios,
      dependentDataset: dependentDataset,
    };

    const request = new HttpRequest('POST', this.apiUrl + endpoint, body, {
      reportProgress: true,
    });
    return this.http
      .request(request)
      .pipe(catchError(this.handleError('get data')));
  }

  uploadDataset(
    file: File | undefined,
    selections: Selections
  ): void {
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

      this.http
        .request(request)
        .pipe(catchError(this.handleError('upload the dataset')))
        .subscribe((event) => {
          if (event.type == HttpEventType.UploadProgress) {
            console.log('uploading');
          }
          if (event.type == HttpEventType.Response) {
            console.log('completed upload');
            this._snackBar.open('Uploaded dataset successfully', 'Close', {
              duration: 4000,
              horizontalPosition: 'end',
              verticalPosition: 'bottom',
            });
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
        selections.datasets.splice(selectedDatasetIndex, 1);
      }
    });
  }

  getAvailableDatasets(selections: Selections): void {
    this.http.get(this.apiUrl + 'data/find_geo').subscribe((datasets) => {
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

  getPossibleFeatures(
    selections: Selections,
    // geoColumn: string,
    datasetId: string | undefined
  ) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );
    this.http
      .post(this.apiUrl + 'data/features', {
        datasetId: datasetId,
        // geoColumn: geoColumn,
      })
      .subscribe((options) => {
        selections.datasets[targetDatasetIdx].possibleFeatures = (
          options as Options
        ).features;
        // selections.datasets[targetDatasetIdx].countryOptions = (
        //   options as Options
        // ).countries;
      });
  }

  getReshapedData(
    selections: Selections,
    datasetId: string | undefined,
    featureSelected: string
  ) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );

    this.http
      .post(this.apiUrl + 'data/reshapecheck', {
        datasetId: datasetId,
        geoColumn: selections.datasets[targetDatasetIdx].geoSelected,
        featureSelected: featureSelected,
      })
      .subscribe((reshapeColumn) => {
        selections.datasets[targetDatasetIdx].reshapeSelected =
          reshapeColumn as string;

        this.getFeatureColumns(selections, datasetId);
      });
  }

  getFeatureColumns(selections: Selections, datasetId: string | undefined) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );

    this.http
      .post(this.apiUrl + 'data/reshape', {
        datasetId: datasetId,
        geoColumn: selections.datasets[targetDatasetIdx].geoSelected,
        reshapeColumn: selections.datasets[targetDatasetIdx].reshapeSelected,
      })
      .subscribe((featureColumns) => {
        selections.datasets[targetDatasetIdx].featureOptions = (
          featureColumns as Options
        ).features;
        selections.datasets[targetDatasetIdx].countryOptions = (
          featureColumns as Options
        ).countries;
        if (selections.datasets[targetDatasetIdx].reshapeSelected !== null) {
          selections.datasets[targetDatasetIdx].timeSelected = 'Time';
        } else {
          selections.datasets[targetDatasetIdx].timeOptions = (
            featureColumns as Options
          ).features;
        }
      });
  }
}
