import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { Dataset, Selections } from 'src/app/types/Datasets';

// settings dialog for advanced column selection

@Component({
  selector: 'app-dataset-settings',
  templateUrl: './dataset-settings.component.html',
  styleUrls: ['./dataset-settings.component.css'],
})
export class DatasetSettingsComponent implements OnInit {
  constructor(
    private dataService: DataService,
    @Inject(MAT_DIALOG_DATA) public datasetId: string
  ) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  public currentDataset?: Dataset;
  public fileName?: string;
  public editMode: boolean = false;
  public currentDatasetIdx?: number;

  onDeleteFile() {
    this.dataService.deleteDataset(this.datasetId, this.selections);
  }

  renameFile() {
    if (this.editMode) {
      this.dataService.renameDataset(
        this.selections,
        this.datasetId,
        this.fileName
      );
    }
    this.editMode = !this.editMode;
  }

  updateReshape() {
    this.dataService.getFeatureColumns(
      this.selections,
      this.datasetId,
      this.currentDataset?.featureSelected!
    );
  }

  updateGeo() {
    if (this.currentDataset?.geoSelected === undefined) {
      this.currentDataset!.geoSelected = 'None';
    }

    this.dataService.updateDataset(this.selections, this.datasetId);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
    this.currentDataset = this.selections.datasets.filter(
      (dataset) => dataset.id == this.datasetId
    )[0];

    this.fileName = this.currentDataset.name;

    this.currentDatasetIdx = this.selections.datasets.findIndex(
      (dataset) => dataset.id === this.datasetId
    );
  }
}
