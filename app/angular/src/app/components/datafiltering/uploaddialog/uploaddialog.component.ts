import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DataService } from 'src/app/services/data.service';
import { Selections } from 'src/app/types/Datasets';

@Component({
  selector: 'app-uploaddialog',
  templateUrl: './uploaddialog.component.html',
  styleUrls: ['./uploaddialog.component.css'],
})
export class UploaddialogComponent implements OnInit {
  constructor(
    private dataService: DataService,
    @Inject(MAT_DIALOG_DATA) public data: Selections
  ) {}

  fileName: string = '';

  fileContent?: File = undefined;

  separator: string = ',';

  onFileSelected(event: any) {
    const file: File = event.target.files[0];

    if (file) {
      this.fileName = file.name;

      this.fileContent = file;

      console.log('new file added');
    }
  }

  onFileUpload() {
    this.dataService.uploadDataset(this.fileContent, this.separator, this.data);
  }

  ngOnInit(): void {}
}
