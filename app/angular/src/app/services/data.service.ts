import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, throwError, catchError } from 'rxjs';
import {
  HttpClient,
  HttpEvent,
  HttpEventType,
  HttpRequest,
  HttpErrorResponse,
  HttpResponse,
} from '@angular/common/http';
import {
  ColumnValues,
  CorrelationMatrix,
  CountryData,
  GraphControls,
} from '../types/GraphData';
import { Dataset, Options, Selections } from '../types/Datasets';
import { MatSnackBar } from '@angular/material/snack-bar';

interface DataLoadingIndicators {
  [datasetId: string]: boolean;
}

// data service for processing datasets on backend

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

  public showLoadingSpinner: DataLoadingIndicators = {};

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
      predictions,
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
      predictions: predictions,
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
    selections: Selections,
    updatedFileName: string
  ): void {
    if (file) {
      const formData = new FormData();

      formData.append('upload', file);

      formData.append('updatedFileName', updatedFileName);

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
      this.apiUrl + 'data/',
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
        this.updateTotalCountries(selections);
        if (
          selections.selectedDataset === datasetId &&
          selections.datasets[0] !== undefined
        ) {
          selections.selectedDataset = selections.datasets[0].id;
        }
        if (
          selections.selectedDataset === datasetId &&
          selections.datasets[0] === undefined
        ) {
          selections.selectedDataset = undefined;
        }
        this.updateDatasetsSelection(selections);
      }
    });
  }

  getAvailableDatasets(selections: Selections): void {
    this.http.get(this.apiUrl + 'data/').subscribe((selectionOptions) => {
      if ((selectionOptions as Dataset[]).length > 0) {
        if (selections.datasets !== undefined) {
          if (
            Object.keys((selectionOptions as Dataset[]).slice(-1)[0]).includes(
              'token'
            )
          ) {
            const idToken = (selectionOptions as Dataset[]).pop();
            localStorage.setItem('id_token', idToken?.token as string);
          }

          for (const dataset of selectionOptions as Dataset[]) {
            if (
              selections.datasets.filter((d) => d.id == dataset.id).length == 0
            ) {
              selections.datasets.push(dataset);
            }
          }
          if (
            selections.selectedDataset === undefined &&
            selections.datasets.length > 0
          ) {
            selections.selectedDataset = selections.datasets[0].id;
          }
        }
      }
    });
  }

  updateTotalCountries(selections: Selections) {
    var countries: string[] = [];
    for (const dataset of selections.datasets) {
      countries = [...countries, ...(dataset.countryOptions || [])];
    }

    selections.totalCountries = [...new Set(countries)].sort();
    if (
      selections.selectedCountry === undefined ||
      !selections.totalCountries.includes(selections.selectedCountry)
    ) {
      selections.selectedCountry = selections.totalCountries[0];
    }
    this.updateDatasetsSelection(selections);
  }

  getFeatureColumns(
    selections: Selections,
    datasetId: string | undefined,
    featureSelected: string
  ) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );

    selections.datasets[targetDatasetIdx].featureSelected = featureSelected;

    this.showLoadingSpinner[datasetId!] = true;

    let timeColumn = selections.datasets[targetDatasetIdx].timeSelected;

    selections.datasets[targetDatasetIdx].timeSelected = undefined;

    this.http
      .post(this.apiUrl + 'data/reshape', {
        datasetId: datasetId,
        geoColumn: selections.datasets[targetDatasetIdx].geoSelected,
        featureSelected: selections.datasets[targetDatasetIdx].featureSelected,
        reshapeSelected: selections.datasets[targetDatasetIdx].reshapeSelected,
      })
      .subscribe((featureColumns) => {
        if (
          selections.datasets[targetDatasetIdx].reshapeSelected === undefined
        ) {
          selections.datasets[targetDatasetIdx].reshapeSelected = (
            featureColumns as Options
          ).reshape_column;
        }

        selections.datasets[targetDatasetIdx].featureOptions = (
          featureColumns as Options
        ).features;
        selections.datasets[targetDatasetIdx].countryOptions = (
          featureColumns as Options
        ).countries;
        selections.datasets[targetDatasetIdx].scope = (
          featureColumns as Options
        ).scope;

        if (selections.datasets[targetDatasetIdx].reshapeSelected !== null) {
          selections.datasets[targetDatasetIdx].timeSelected = 'Time';
        } else {
          selections.datasets[targetDatasetIdx].timeOptions = (
            featureColumns as Options
          ).features;

          selections.datasets[targetDatasetIdx].timeSelected = timeColumn;
        }

        if (selections.datasets[targetDatasetIdx].timeSelected !== undefined) {
          this.updateDatasetsSelection(selections);
          this.updateTotalCountries(selections);
        }
        this.showLoadingSpinner[datasetId!] = false;
      });
  }

  updateDataset(selections: Selections, datasetId: string | undefined) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );

    this.http
      .post(this.apiUrl + 'data/update', {
        datasetId: datasetId,
        geoColumn: selections.datasets[targetDatasetIdx].geoSelected,
        featureSelected: selections.datasets[targetDatasetIdx].featureSelected,
        reshapeSelected: selections.datasets[targetDatasetIdx].reshapeSelected,
        datasetName: selections.datasets[targetDatasetIdx].name,
      })
      .subscribe((data) => {
        if (Object.keys(data).length > 0) {
          selections.datasets[targetDatasetIdx] = data as Dataset;
        }

        this.updateDatasetsSelection(selections);
      });
  }

  renameDataset(
    selections: Selections,
    datasetId: string | undefined,
    updatedName: string | undefined
  ) {
    const targetDatasetIdx = selections.datasets.findIndex(
      (dataset) => dataset.id == datasetId
    );

    this.http
      .post(this.apiUrl + 'data/name', {
        datasetName: updatedName,
        datasetId: datasetId,
      })
      .subscribe((response) => {
        selections.datasets[targetDatasetIdx].name = updatedName;

        this.updateDatasetsSelection(selections);
      });
  }
}
