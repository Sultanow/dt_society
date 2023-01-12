import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { UploaddialogComponent } from '../uploaddialog/uploaddialog.component';
import { Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-fileupload',
  templateUrl: './fileupload.component.html',
  styleUrls: ['./fileupload.component.css'],
})
export class FileuploadComponent implements OnInit {
  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  constructor(private dataService: DataService, public dialog: MatDialog) {}

  getDemoDatasets() {
    this.dataService.getDemoData(this.selections);
  }

  onFileUpload(event: any) {
    this.dialog.open(UploaddialogComponent);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
