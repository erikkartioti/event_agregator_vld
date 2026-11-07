package com.eventagregatornew.eventagregatornew.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import com.eventagregatornew.eventagregatornew.service.EventService;

@Controller
public class MapController {

    @Autowired
    private EventService eventService;
    
    @GetMapping("/database")
    public String showMap(Model model) {
        // Fetch events from your PostgreSQL database through the service
        model.addAttribute("events", eventService.getAllEvents());
        // Returning "map" tells Spring to resolve the view, e.g. src/main/resources/templates/map.html
        return "database";
    }

    @GetMapping("/map")
    public String showInteractiveMap(Model model) {
        model.addAttribute("events", eventService.getAllEvents());
        return "map"; // Вернет src/main/resources/templates/map.html
        }
    }

