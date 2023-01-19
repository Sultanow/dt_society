import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { Dataset, Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-vardatasetsettings',
  templateUrl: './vardatasetsettings.component.html',
  styleUrls: ['./vardatasetsettings.component.css'],
})
export class VarDatasetSettingsComponent implements OnInit {
  constructor(
    private dataService: DataService,
    @Inject(MAT_DIALOG_DATA) public data: { datasetId: string; type: string }
  ) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };
  featureList?: string[];

  public currentDataset?: Dataset;

  public featuresSelected?: string[];

  updateFeatureSelections() {
    if (
      (this.featuresSelected?.length === 1 &&
        this.featuresSelected[0] === this.currentDataset?.featureSelected) ||
      this.featuresSelected?.length === 0
    ) {
      this.featuresSelected = [];
      this.featuresSelected.push(this.currentDataset!.featureSelected!);
      if (this.data.type === 'graph') {
        this.currentDataset!.varFeaturesSelected = undefined;
      } else if (this.data.type === 'map') {
        this.currentDataset!.varmapFeaturesSelected = undefined;
      }
    } else {
      if (this.data.type === 'graph') {
        this.currentDataset!.varFeaturesSelected = this.featuresSelected;
      } else if (this.data.type === 'map') {
        this.currentDataset!.varmapFeaturesSelected = this.featuresSelected;
      }
    }
    this.dataService.updateDatasetsSelection(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
    this.currentDataset = this.selections.datasets.filter(
      (dataset) => dataset.id == this.data.datasetId
    )[0];
    this.featureList = this.currentDataset.featureOptions!.filter(
      (feature) => feature !== this.currentDataset!.timeSelected
    );

    this.featuresSelected = [];

    if (this.data.type === 'graph') {
      if (this.currentDataset.varFeaturesSelected !== undefined) {
        this.featuresSelected = this.currentDataset.varFeaturesSelected;
      } else {
        this.featuresSelected.push(this.currentDataset.featureSelected!);
      }
    } else if (this.data.type === 'map') {
      if (this.currentDataset.varmapFeaturesSelected !== undefined) {
        this.featuresSelected = this.currentDataset.varmapFeaturesSelected;
      } else {
        this.featuresSelected.push(this.currentDataset.featureSelected!);
      }
    }
  }
}
