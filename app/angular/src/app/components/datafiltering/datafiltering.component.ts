import { Component, OnInit } from '@angular/core';
import { Selections } from '../../types/Datasets';
import { DataService } from 'src/app/services/data.service';
import { MatDialog } from '@angular/material/dialog';
import { UploaddialogComponent } from './uploaddialog/uploaddialog.component';
import { faGear } from '@fortawesome/free-solid-svg-icons';
import { DatasetSettingsComponent } from './dataset-settings/dataset-settings.component';
import { ReplaySubject } from 'rxjs';

interface DataLoadingIndicators {
  [datasetId: string]: boolean;
}

// sidebar navigation component for filtering and selection of data

@Component({
  selector: 'app-datafiltering',
  templateUrl: './datafiltering.component.html',
  styleUrls: ['./datafiltering.component.css'],
})
export class DatafilteringComponent implements OnInit {
  constructor(public dataService: DataService, public dialog: MatDialog) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
    totalCountries: [],
  };

  public filteredCountries: ReplaySubject<string[] | undefined> =
    new ReplaySubject<string[] | undefined>(1);

  settingsIcon = faGear;

  public showLoadingSpinner: DataLoadingIndicators = {};

  updateSelectedColumns(
    filename: string | undefined,
    value: string,
    column: string
  ) {
    if (this.selections.datasets.length > 0) {
      const datasetIndex = this.selections.datasets
        .map((d) => d.id)
        .indexOf(filename);

      switch (column) {
        case 'time':
          this.dataService.updateTotalCountries(this.selections);
          break;
        case 'feature':
          this.selections.datasets[datasetIndex].reshapeSelected = undefined;
          this.dataService.getFeatureColumns(this.selections, filename, value);
      }
    }
  }

  drop(event: any) {
    console.log(event);
  }

  updateSelectedCountry(selectedCountry: string) {
    this.selections.selectedCountry = selectedCountry;
    this.dataService.updateDatasetsSelection(this.selections);
  }

  onFileUpload(event: any) {
    this.dialog.open(UploaddialogComponent, { data: this.selections });
  }

  onDeleteFile(datasedId: string | undefined) {
    this.dataService.deleteDataset(datasedId, this.selections);
  }

  updateSideBar() {
    this.dataService.updateDatasetsSelection(this.selections);
  }

  onSettings(datasetId: string | undefined) {
    this.dialog.open(DatasetSettingsComponent, { data: datasetId });
  }

  getDatasetStatus(dataset_id: string | undefined): string {
    if (
      this.selections.selectedCountry === undefined ||
      dataset_id === undefined
    ) {
      return 'inactive';
    }
    let dataset = this.selections.datasets.filter(
      (dataset) => dataset.id == dataset_id
    )[0];
    if (dataset.countryOptions?.includes(this.selections.selectedCountry)) {
      return 'active';
    }
    return 'inactive';
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;

      this.selections.datasets.map((dataset) => {
        if (dataset.id !== undefined) {
          this.dataService.showLoadingSpinner[dataset.id] = false;
        }
      });

      this.filteredCountries.next(this.selections.totalCountries);
    });
    this.dataService.getAvailableDatasets(this.selections);
  }

  protected filterCountries(event: any) {
    if (!this.selections.totalCountries) {
      return;
    }
    let search = event;
    if (!search) {
      this.filteredCountries.next(this.selections.totalCountries);
      return;
    } else {
      search = search.toLowerCase();
    }

    this.filteredCountries.next(
      this.selections.totalCountries.filter((country) =>
        country!.toLowerCase().includes(search)
      )
    );
  }
}
