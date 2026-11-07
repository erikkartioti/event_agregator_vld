// src/main/java/com/eventagregatornew/eventagregatornew/model/GeolocationEntity.java

package com.eventagregatornew.eventagregatornew.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "geolocation")
public class GeoLocationEntity { 
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "location_name", nullable = false)
    private String locationName;

    @Column(name = "address", nullable = false)
    private String address;

    @Column(name = "longitude", nullable = false)
    private Double longitude;

    @Column(name = "latitude", nullable = false)
    private Double latitude;

    // Default constructor for JPA
    public GeoLocationEntity() { 
    }

    public GeoLocationEntity(String locationName, String address, Double longitude, Double latitude) { 
        this.locationName = locationName;
        this.address = address;
        this.longitude = longitude;
        this.latitude = latitude;
    }

    // Getters and Setters (остаются прежними, так как они ссылаются на поля класса)
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getLocationName() {
        return locationName;
    }

    public void setLocationName(String locationName) {
        this.locationName = locationName;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public Double getLongitude() {
        return longitude;
    }

    public void setLongitude(Double longitude) {
        this.longitude = longitude;
    }

    public Double getLatitude() {
        return latitude;
    }

    public void setLatitude(Double latitude) {
        this.latitude = latitude;
    }

    @Override
    public String toString() {
        return "GeoLocationEntity{" + 
               "id=" + id +
               ", locationName='" + locationName + '\'' +
               ", address='" + address + '\'' +
               ", longitude=" + longitude +
               ", latitude=" + latitude +
               '}';
    }
}