import { Component, OnInit } from '@angular/core';
import { Selections } from '../../types/Datasets';
import { DataService } from 'src/app/services/data.service';
import { MatDialog } from '@angular/material/dialog';
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
    column: string
  ) {
    if (this.selections.datasets.length > 0) {
      const datasetIndex = this.selections.datasets
        .map((d) => d.id)
        .indexOf(filename);

      switch (column) {
        case 'time':
          this.selections.datasets[datasetIndex].timeSelected = value;
          break;
        case 'feature':
          this.selections.datasets[datasetIndex].featureSelected = value;
          this.dataService.getReshapedData(this.selections, filename, value);
      }

      this.dataService.updateDatasetsSelection(this.selections);
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

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });

    this.dataService.getAvailableDatasets(this.selections);
  }
}
