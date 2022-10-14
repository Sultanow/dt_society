import { Component, OnInit } from '@angular/core';
import { DataService } from 'src/app/services/data.service';


@Component({
  selector: 'app-correlation',
  styleUrls: ['./correlation.component.css'],
  template: '<plotly-plot [data]="data.data" [layout]="data.layout"></plotly-plot>'

})
export class CorrelationComponent implements OnInit {

  constructor(private dataService: DataService) { }

  public data = {
    data: [],
    layout: {},

  };

  public columns = {
    geo: ["geo\\time", "geo\\time"],
    x: ["Time", "Time"],
    rshp: ["age", "unit"],
  }

  ngOnInit(): void {
    this.dataService.getData(this.columns, "graph/corr").subscribe(data => this.data = {
      data: (data as any).data,
      layout: (data as any).layout
    });
  }

}
