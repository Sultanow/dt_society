import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-varforecasts',
  templateUrl: './varforecasts.component.html',
  styleUrls: ['./varforecasts.component.css'],
})
export class VarforecastsComponent implements OnInit {
  constructor(private dataService: DataService) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((data) => {
      this.selections = data;
    });
  }
}
