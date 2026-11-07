package com.eventagregatornew.eventagregatornew.service;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.eventagregatornew.eventagregatornew.model.EventEntity;
import com.eventagregatornew.eventagregatornew.repository.EventRepository;

@Service
public class EventService {

    @Autowired
    private EventRepository eventRepository;
    
    public List<EventEntity> getAllEvents() {
        return eventRepository.findAll();
    }
}