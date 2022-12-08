import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-uploaddialog',
  templateUrl: './uploaddialog.component.html',
  styleUrls: ['./uploaddialog.component.css'],
})
export class UploaddialogComponent implements OnInit {
  constructor(private dataService: DataService) {}

  fileName: string = '';

  fileContent?: File = undefined;

  selections: Selections = {
    datasets: [],
    selectedDataset: undefined,
  };

  onFileSelected(event: any) {
    const file: File = event.target.files[0];

    if (file) {
      this.fileName = file.name;

      this.fileContent = file;

      console.log('new file added');
    }
  }

  onFileUpload() {
    this.dataService.uploadDataset(this.fileContent, this.selections);
  }

  ngOnInit(): void {
    this.dataService.currentSelections.subscribe((value) => {
      this.selections = value;
    });
  }
}
