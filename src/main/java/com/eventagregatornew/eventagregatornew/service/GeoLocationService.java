package com.eventagregatornew.eventagregatornew.service;

import com.eventagregatornew.eventagregatornew.model.GeoLocationEntity;
import com.eventagregatornew.eventagregatornew.repository.GeoLocationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class GeoLocationService {
    
    @Autowired
    private GeoLocationRepository repository;
    
    public List<GeoLocationEntity> getAll() {
        return repository.findAll();
    }
}