package com.eventagregatornew.eventagregatornew.repository;

import com.eventagregatornew.eventagregatornew.model.GeoLocationEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface GeoLocationRepository extends JpaRepository<GeoLocationEntity, Long> {
    List<GeoLocationEntity> findByLocationName(String locationName);
    Optional<GeoLocationEntity> findByLocationNameAndAddress(String locationName, String address);
}