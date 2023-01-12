import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

// wrapper component for correlation component

@Component({
  selector: 'app-correlations',
  templateUrl: './correlations.component.html',
  styleUrls: ['./correlations.component.css'],
})
export class CorrelationsComponent implements OnInit {
  constructor(private dataService: DataService, public dialog: MatDialog) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  public validDatasetAvailable: boolean = false;

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
      if (
        this.selections.datasets.some(
          (dataset) =>
            dataset.timeSelected !== undefined &&
            dataset.featureSelected !== undefined
        )
      ) {
        this.validDatasetAvailable = true;
      } else {
        this.validDatasetAvailable = false;
      }
    });
  }
}
