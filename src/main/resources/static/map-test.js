    // Styling function based on common feature properties
    function googleLikeStyle(feature, resolution) {
        const geometryType = feature.getGeometry().getType();
        const properties = feature.getProperties();
        const styles = [];
      
        // Hide specific landuse types
        if (properties['landuse'] === 'military' 
        || properties['landuse'] === 'allotments' 
        || properties['landuse'] === 'residential' 
        || properties['landuse'] === 'construction'
        || properties['landuse'] === 'landfill' 
        || properties['landuse'] === 'industrial' 
        || properties['landuse'] === 'commercial' 
        || properties['landuse'] === 'retail' 
        || properties['landuse'] === 'garages'
        || properties['landuse'] === 'railway'
        || properties['landuse'] === 'quarry'
        || properties['landuse'] === 'greenhouse_horticulture'
        || properties['landuse'] === 'recreation_ground'
        || properties['landuse'] === 'brownfield') {
          return []; 
        }
      
        if (properties['highway'] === 'footway' 
        || properties['highway'] === 'steps' 
        || properties['barrier'] 
        || properties['railway']
        || properties['waterway'] === 'river'
        || properties['other_tags'] === 'boundary'
        || properties['waterway'] === 'canal'
        || properties['wires']) {
          return []; 
        }
      
        /* if (properties['landuse'] === 'farmland' 
        || properties['landuse'] === 'orchard' 
        || properties['landuse'] === 'forest' 
        || properties['natural'] === 'scree') {
          return []; 
        }
        */
      
        if (properties['amenity']==='parking' 
        || properties['amenity'] === 'school' 
        || properties['amenity'] === 'college' 
        || properties['amenity'] === 'post_office' 
        || properties['amenity'] === 'hospital' 
        || properties['amenity'] === 'marketplace' 
        || properties['amenity'] === 'restaurant'
        || properties['amenity'] === 'kindergarten'
        || properties['amenity'] === 'university'
        || properties['amenity'] === 'police') {
          return []; 
        }
      
        if (properties['place'] === 'city' 
        || properties['place'] === 'town'
        || properties['place'] === 'suburb'
        || properties['place'] === 'village'
        || properties['place'] === 'locality'
        || properties['place'] === 'neighbourhood'
        || properties['place'] === 'square') {
          return []; 
        }
      
        if (properties['boundary']==='administrative'
        || properties['boundary']==='protected_area') {
          return []; 
        }
      
        if (properties['leisure']==='stadium'
        || properties['leisure']==='sports_centre'
        || properties['natural']==='fell'
        || properties['shop']==='greengrocer'){
          return [];
        }
      
        const zoom = map.getView().getZoom();
      
        const colors = {
          road: 'rgba(200, 200, 200, 0.8)',
          building: 'rgba(180, 180, 180, 1)',
          buildingAlpha: 'rgba(0, 0, 0, 0)',
          park: 'rgba(170, 240, 170, 0.6)', // park, gras, greenfield, meadow, heath, scrub
          forest: 'rgba(0, 128, 0, 0.4)', // Green for forests and wood
          cemetery: 'rgba(0, 110, 0, 0.5)',// Other green for cemeteries
          water: 'rgba(170, 205, 255, 1)',
        };
      
        // Check zoom level and style accordingly
        const showTextAtZoomLevel = 15; // Show street names at zoom level 15 and above
        const showBuildingsAtZoomLevel = 16; // Show buildings at zoom level 16 and above
      
        if (geometryType === 'Polygon' || geometryType === 'MultiPolygon') {
          if (properties['landuse'] === 'park'
          || properties['landuse'] === 'greenfield'  
          || properties['landuse'] === 'meadow' 
          || properties['landuse'] === 'farmland' 
          || properties['landuse'] === 'grass'
          || properties['landuse'] === 'orchard' 
          || properties['landuse'] === 'forest'
          || properties['leisure'] === 'park' 
          || properties['leisure'] === 'garden'
          || properties['leisure'] === 'pitch' // football fields 
          || properties['natural'] === 'scree'
          || properties['natural'] === 'grassland'
          || properties['natural'] === 'scrub'
          || properties['natural'] === 'heath') {
            styles.push(new ol.style.Style({
              fill: new ol.style.Fill({ color: colors.park }),
              stroke: null // Hide stroke for polygons and multipolygons
            }));
          } else if (properties['natural'] === 'wood') {
            styles.push(new ol.style.Style({
              fill: new ol.style.Fill({ color: colors.forest }), // Green for both forest and wood
              stroke: null // Hide stroke for polygons and multipolygons
            }));
      
          } else if (properties['landuse'] === 'cemetery') {
            styles.push(new ol.style.Style({
              fill: new ol.style.Fill({ color: colors.cemetery }), // Other green for cemetery
              stroke: null // Hide stroke for polygons and multipolygons
            }));
      
      
          /* } else if (properties['building'] && zoom <= showBuildingsAtZoomLevel) {
              return [];
            }
          */
      
          } else if (properties['building'] && zoom >= showBuildingsAtZoomLevel) {
            styles.push(new ol.style.Style({
              fill: new ol.style.Fill({ color: colors.building }),
              stroke: null
            }));
      
          } else if (properties['building'] && zoom < showBuildingsAtZoomLevel && zoom > 5) {
            styles.push(new ol.style.Style({
              fill: new ol.style.Fill({ color: colors.buildingAlpha }),
              stroke: null
            }));
          
          } else if (properties['natural'] === 'water') {
            styles.push(new ol.style.Style({
              fill: new ol.style.Fill({ color: colors.water }),
              stroke: null // Hide stroke for polygons and multipolygons
            }));
          } else {
            // For other polygons and multipolygons, hide wireframe until zoom level 16
            if (zoom < showBuildingsAtZoomLevel) {
              styles.push(new ol.style.Style({
                fill: new ol.style.Fill({ color: colors.road }),
                stroke: null // Hide stroke for polygons and multipolygons
              }));
            } else {
              styles.push(new ol.style.Style({
                fill: new ol.style.Fill({ color: colors.road }),
                stroke: null // Hide stroke until zoom level 16
              }));
            }
          }
        } else if (geometryType === 'LineString') {
          if (zoom >= showTextAtZoomLevel) {
            styles.push(new ol.style.Style({
              stroke: new ol.style.Stroke({
                color: colors.road,
                width: 2
              }),
              text: new ol.style.Text({
                text: properties.name || '', // Assuming "name" property holds street names
                font: '12px Calibri,sans-serif',
                fill: new ol.style.Fill({ color: '#333' }),
                stroke: new ol.style.Stroke({ color: '#fff', width: 2 }),
                placement: 'line', // Make text follow the road
              })
            }));
          } else {
            styles.push(new ol.style.Style({
              stroke: new ol.style.Stroke({
                color: colors.road,
                width: 2
              })
            }));
          }
        }
      
        return styles;
      }
      
          // Initialize the map
          var map = new ol.Map({
            target: 'map',
            layers: [
              new ol.layer.VectorTile({
                source: new ol.source.VectorTile({
                  format: new ol.format.MVT(),
                  url: 'http://localhost:9090/data/tiles/{z}/{x}/{y}.pbf'
                }),
                style: googleLikeStyle
              })
            ],
            view: new ol.View({
              center: ol.proj.fromLonLat([44.6534, 42.9837]),
              zoom: 12
            })
          });

          // Toggle panel visibility
function togglePanel() {
    const panel = document.getElementById('dataPanel');
    panel.classList.toggle('active');
  }
          