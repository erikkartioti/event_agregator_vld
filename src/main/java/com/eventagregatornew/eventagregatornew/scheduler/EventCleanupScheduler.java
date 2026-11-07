package com.eventagregatornew.eventagregatornew.scheduler;

import java.time.LocalDateTime;
import java.time.ZoneId;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import com.eventagregatornew.eventagregatornew.repository.EventRepository;

@Component
@ConditionalOnProperty(name = "app.schedulers.enabled", havingValue = "true", matchIfMissing = true)
public class EventCleanupScheduler {
    
    private final EventRepository eventRepository;

    public EventCleanupScheduler(EventRepository eventRepository) {
        this.eventRepository = eventRepository;
    }

    @Scheduled(cron = "0 34 00 * * *", zone = "Europe/Moscow") 
    public void cleanUpOldEvents() {
        LocalDateTime now = LocalDateTime.now(ZoneId.of("Europe/Moscow"));
        int deletedCount = eventRepository.deleteByDateBefore(now);
        System.out.println("Deleted " + deletedCount + " outdated events.");
    }
}

