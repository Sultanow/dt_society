import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

// wrapper component for table, stats, history and map
@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css'],
})
export class OverviewComponent implements OnInit {
  constructor(private dataService: DataService, public dialog: MatDialog) {}

  public geoData: boolean = true;

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((data) => {
      this.selections = data;

      let datasetId = this.selections.datasets.findIndex(
        (dataset) => dataset.id == this.selections.selectedDataset
      );
      let currentDataset = this.selections.datasets[datasetId];
      if (
        currentDataset !== undefined &&
        currentDataset.featureSelected !== undefined
      ) {
        if (currentDataset.geoSelected === 'None') {
          this.geoData = false;
        } else {
          this.geoData = true;
        }
      }
    });
  }
}
