import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-varforecasts',
  templateUrl: './varforecasts.component.html',
  styleUrls: ['./varforecasts.component.css'],
})
export class VarforecastsComponent implements OnInit {
  constructor(private dataService: DataService, private router: Router) {}

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  public activeRouteName: string = '';

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((data) => {
      this.selections = data;
    });

    this.activeRouteName = this.router.url.slice(
      this.router.url.lastIndexOf('var') + 4
    );
  }
}
