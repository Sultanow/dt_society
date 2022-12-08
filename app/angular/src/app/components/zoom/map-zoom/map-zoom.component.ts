import { Options } from '@angular-slider/ngx-slider';
import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { Frame, GraphData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-map-zoom',
  templateUrl: './map-zoom.component.html',
  styleUrls: ['./map-zoom.component.css'],
})
export class MapZoomComponent implements OnInit {
  constructor() {}

  public data: GraphData = {
    data: [],
    layout: {},
    config: { responsive: true },
  };

  public plotData: GraphData = {
    data: [],
    layout: {},
    config: { responsive: true },
  };

  ngOnInit(): void {
    this.data = structuredClone(this.plotData);
    this.data.layout.width = 1400;
    this.data.layout.height = 1000;
    console.log(Object.keys(this.data.data[0]));
    console.log(this.data.data[0]['zoom' as keyof Object]);
  }
}
