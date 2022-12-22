import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { GraphData } from 'src/app/types/GraphData';

@Component({
  selector: 'app-map-zoom',
  templateUrl: './map-zoom.component.html',
  styleUrls: ['./map-zoom.component.css'],
})
export class MapZoomComponent implements OnInit {
  constructor(@Inject(MAT_DIALOG_DATA) public plotData: GraphData) {}

  public data: GraphData = {
    data: [],
    layout: {},
    config: { responsive: true },
  };

  ngOnInit(): void {
    this.data = structuredClone(this.plotData);
    this.data.layout.width = 1400;
    this.data.layout.height = 1000;
    this.data.layout.mapbox.zoom = 3;
  }
}
