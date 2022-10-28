import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Selections } from '../../types/Datasets';
import { DataService } from 'src/app/services/data.service';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { UploaddialogComponent } from './uploaddialog/uploaddialog.component';

@Component({
  selector: 'app-datafiltering',
  templateUrl: './datafiltering.component.html',
  styleUrls: ['./datafiltering.component.css'],
})
export class DatafilteringComponent implements OnInit {
  constructor(private dataService: DataService, public dialog: MatDialog) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  fileName = '';

  updateSelectedColumns(
    filename: string | undefined,
    value: string,
    column: string,
    reshape?: boolean
  ) {
    if (this.selections.datasets.length > 0) {
      const datasetIndex = this.selections.datasets
        .map((d) => d.id)
        .indexOf(filename);

      switch (column) {
        case 'geo':
          this.selections.datasets[datasetIndex].geoSelected = value;
          break;
        case 'rshp':
          this.selections.datasets[datasetIndex].reshapeSelected = value;
          this.dataService.getReshapedData(this.selections, filename, reshape);
          break;
        case 'x':
          this.selections.datasets[datasetIndex].timeSelected = value;
          this.selections.datasets[datasetIndex].featureOptions =
            this.selections.datasets[datasetIndex].featureOptions?.filter(
              (feature) => feature !== value
            );
          break;
        case 'y':
          this.selections.datasets[datasetIndex].featureSelected = value;
      }

      this.dataService.updateDatasetsSelection(this.selections);
    }
  }

  onFileUpload(event: any) {
    this.dialog.open(UploaddialogComponent, { data: this.selections });
  }

  onDeleteFile(datasedId: string | undefined) {
    this.dataService.deleteDataset(datasedId, this.selections);
  }

  reshapeOptions(
    datasetId: string | undefined,
    reshape: boolean,
    event: any
  ): void {
    this.dataService.getReshapedData(this.selections, datasetId, event.checked);
    this.dataService.updateDatasetsSelection(this.selections);
  }

  changeFocus() {
    this.dataService.updateDatasetsSelection(this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });

    this.dataService.getAvailableDatasets(this.selections);
  }
}
