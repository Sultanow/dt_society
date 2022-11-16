import { Component } from '@angular/core';
import { Selections } from './types/Datasets';
import { DataService } from 'src/app/services/data.service';
import { HttpClient } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { UploaddialogComponent } from 'src/app/components/datafiltering/uploaddialog/uploaddialog.component';
import {
  faChartColumn,
  faChartSimple,
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Digital Twin of Society';

  constructor(
    private dataService: DataService,
    private http: HttpClient,
    public dialog: MatDialog
  ) {}

  selectedDatasets: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  public faChartColumn = faChartSimple;

  getDemoDatasets() {
    this.dataService.getDemoData(this.selectedDatasets);
  }

  onFileUpload(event: any) {
    this.dialog.open(UploaddialogComponent);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selectedDatasets = value;
    });
  }
}
