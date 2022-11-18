import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  DetachedRouteHandle,
  RouteReuseStrategy,
  UrlSegment,
} from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class RoutecachingService implements RouteReuseStrategy {
  cache: { [key: string]: DetachedRouteHandle } = {};

  // Checks whether route should be cached
  shouldDetach(route: ActivatedRouteSnapshot): boolean {
    return route.data['reuse'] === true;
  }

  //stores the route in chache
  store(route: ActivatedRouteSnapshot, handle: DetachedRouteHandle): void {
    if (route.data['reuse']) {
      this.cache[route.toString()] = handle;
    }
  }

  //check whether to get route form cache or load new
  shouldAttach(route: ActivatedRouteSnapshot): boolean {
    const handle = this.cache[route.toString()];
    const canAttach = route.data['reuse'] && !!handle;
    return canAttach;
  }

  //get route from cache if shouldAttach is true
  retrieve(route: ActivatedRouteSnapshot): DetachedRouteHandle | null {
    if (!route.data['reuse'] || !this.cache[route.toString()]) {
      return null;
    }
    return this.cache[route.toString()];
  }

  shouldReuseRoute(
    future: ActivatedRouteSnapshot,
    curr: ActivatedRouteSnapshot
  ): boolean {
    return future.routeConfig === curr.routeConfig;
  }
}
