import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-fileupload',
  templateUrl: './fileupload.component.html',
  styleUrls: ['./fileupload.component.css'],
})
export class FileuploadComponent implements OnInit {
  fileName = '';

  constructor(private httpClient: HttpClient) {}

  onFileSelected(event: any) {
    const file: File = event.target.files[0];

    if (file) {
      this.fileName = file.name;

      const formData = new FormData();

      formData.append('upload', file);

      const upload$ = this.httpClient.post('http://127.0.0.1:5000/', formData);

      upload$.subscribe();
    }
  }

  ngOnInit(): void {}
}
