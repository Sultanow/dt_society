import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';

@Component({
  selector: 'app-history',
  //templateUrl: './history.component.html',
  styleUrls: ['./history.component.css'],
  template: '<plotly-plot [data]="data.data" [layout]="data.layout"></plotly-plot>'
})
export class HistoryComponent implements OnInit {

  constructor(private dataService: DataService) { }

  public data = {
    data: [],
    layout: {},

  };

  public columns = {
    geo: ["geo\\time"],
    x: ["Time"],
    rshp: ["age"],
    y: ["Y15-74"],
    id: 0,

  }

  ngOnInit(): void {
    this.dataService.getData(this.columns, "/graph/history").subscribe(data => this.data = {
      data: (data as any).data,
      layout: (data as any).layout
    });
  }

}
