import { Component } from '@angular/core';
import { Selections } from './types/Datasets';
import { DataService } from 'src/app/services/data.service';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Digital Twin of Society';

  constructor(private dataService: DataService, private http: HttpClient) {}

  selectedDatasets: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  getDemoDatasets() {
    this.dataService.getDemoData(this.selectedDatasets);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
  }
}
