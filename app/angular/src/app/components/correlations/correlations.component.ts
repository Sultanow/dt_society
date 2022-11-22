import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-correlations',
  templateUrl: './correlations.component.html',
  styleUrls: ['./correlations.component.css']
})
export class CorrelationsComponent implements OnInit {
  constructor(private dataService: DataService, public dialog: MatDialog) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
