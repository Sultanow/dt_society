import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Dataset, Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-dataset-settings',
  templateUrl: './dataset-settings.component.html',
  styleUrls: ['./dataset-settings.component.css'],
})
export class DatasetSettingsComponent implements OnInit {
  public datasetId?: string;
  public geoEnabled: boolean = true;
  constructor(private dataService: DataService) {}

  public currentDataset?: Dataset;
  public editMode: boolean = false;

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  onDeleteFile() {
    this.dataService.deleteDataset(this.datasetId, this.selections);
  }

  toggleEditMode() {
    this.editMode = !this.editMode;
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
    this.currentDataset = this.selections.datasets.filter(
      (dataset) => dataset.id == this.datasetId
    )[0];
  }

  saveDatasetSettings() {
    if (this.currentDataset?.geoSelected === undefined) {
      this.currentDataset!.geoSelected = 'None';
    }

    this.dataService.updateDataset(this.selections, this.datasetId);
  }
}
