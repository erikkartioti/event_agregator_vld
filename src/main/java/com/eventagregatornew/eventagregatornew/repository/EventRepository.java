package com.eventagregatornew.eventagregatornew.repository;

import java.time.LocalDateTime;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;

import com.eventagregatornew.eventagregatornew.model.EventEntity;

public interface EventRepository extends JpaRepository<EventEntity, Long> {
    // Spring Data JPA will automatically implement basic CRUD operations.

    @Transactional
    int deleteByDateBefore(LocalDateTime date);
}
