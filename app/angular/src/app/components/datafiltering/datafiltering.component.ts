import { Component, OnInit } from '@angular/core';
import { Selections } from '../../types/Datasets';
import { DataService } from 'src/app/services/data.service';
import { MatDialog } from '@angular/material/dialog';
import { UploaddialogComponent } from './uploaddialog/uploaddialog.component';
import {
  faGear
} from '@fortawesome/free-solid-svg-icons';
import { DatasetSettingsComponent } from './dataset-settings/dataset-settings.component';
import { ReplaySubject } from 'rxjs';

@Component({
  selector: 'app-datafiltering',
  templateUrl: './datafiltering.component.html',
  styleUrls: ['./datafiltering.component.css'],
})
export class DatafilteringComponent implements OnInit {
  constructor(private dataService: DataService, public dialog: MatDialog) {}

  settingsIcon = faGear;

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
    totalCountries: [],
  };

  public filteredCountries: ReplaySubject<string[] | undefined> =
    new ReplaySubject<string[] | undefined>(1);

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
          this.selections.datasets[datasetIndex].timeSelected = value;
          this.dataService.updateTotalCountries(this.selections);
          break;
        case 'feature':
          this.dataService.getFeatureColumns(this.selections, filename, value);
      }
    }
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

  changeFocus() {
    this.dataService.updateDatasetsSelection(this.selections);
  }

  updateCountry() {
    this.dataService.updateDatasetsSelection(this.selections);
  }

  onSettings(datasedId: string | undefined){
    let dialogRef = this.dialog.open(DatasetSettingsComponent)
    dialogRef.componentInstance.datasetId = datasedId;
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      this.filteredCountries.next(this.selections.totalCountries);
    });
    this.dataService.getAvailableDatasets(this.selections);
  }

  protected filterCountries(event: any){
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
