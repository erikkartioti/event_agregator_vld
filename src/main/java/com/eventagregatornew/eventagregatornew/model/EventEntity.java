package com.eventagregatornew.eventagregatornew.model;

import java.time.LocalDateTime;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name="events")
public class EventEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String title;
    private LocalDateTime date; // For a real app, consider using java.time.LocalDateTime
    private String genre;
    private String age_restriction;
    private String location;
    private String details;
    private String scene;
 

    // Getters and setters (or use Lombok's @Data for brevity)
    
    public Long getId() {
        return id;
    }
    public void setId(Long id) {
        this.id = id;
    }
    public String getTitle() {
        return title;
    }
    public void setTitle(String title) {
        this.title = title;
    }
    public String getLocation() {
        return location;
    }
    public void setLocation(String location) {
        this.location = location;
    }
    public LocalDateTime getDate() {
        return date;
    }
    public void setDate(LocalDateTime date) {
        this.date = date;
    }

    public String getGenre() {
        return genre;
    }
    public void setGenre(String genre) {
        this.genre = genre;
    }

    public String getAge_restriction() {
        return age_restriction;
    }
    public void setAge_restriction(String age_restriction) {
        this.age_restriction = age_restriction;
    }

    public String getDetails() {
        return details;
    }
    public void setDetails(String details) {
        this.details = details;
    }

    public String getScene() {
        return scene;
    }
    public void setScene(String scene) {
        this.scene = scene;
    }
}

