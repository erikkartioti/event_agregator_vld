package com.eventagregatornew.eventagregatornew.assistant;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.*;

/**
 * Ассистент не пишет в БД сам: он возвращает черновик события (с координатами),
 * а пользователь подтверждает его в UI, и фронт вызывает обычный POST /api/events.
 */
@RestController
@RequestMapping("/api/assistant")
public class AssistantController {

    public record ChatRequest(List<Map<String, String>> messages) {}

    private final QwenClient qwen;
    private final GeocodingService geo;
    private final ObjectMapper mapper = new ObjectMapper();

    public AssistantController(QwenClient qwen, GeocodingService geo) {
        this.qwen = qwen;
        this.geo = geo;
    }

    @PostMapping
    public Map<String, Object> chat(@RequestBody ChatRequest req) throws Exception {
        if (req.messages() == null || req.messages().isEmpty() || req.messages().size() > 30) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "bad messages");
        }
        JsonNode msg = qwen.complete(req.messages());
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("action", null);

        JsonNode calls = msg.path("tool_calls");
        if (!calls.isArray() || calls.isEmpty()) {
            out.put("reply", msg.path("content").asText("Не понял запрос, повторите, пожалуйста."));
            return out;
        }

        JsonNode fn = calls.get(0).path("function");
        if (!"create_event".equals(fn.path("name").asText())) {
            out.put("reply", "Я умею только создавать события.");
            return out;
        }
        JsonNode args = mapper.readTree(fn.path("arguments").asText("{}"));
        String title = args.path("title").asText("").trim();
        String street = args.path("street").asText("").trim();

        LocalDateTime start;
        try {
            start = LocalDateTime.parse(args.path("start_time").asText());
        } catch (Exception e) {
            out.put("reply", "Не смог разобрать время. Напишите дату и время точнее, например «14 ноября в 19:00».");
            return out;
        }
        if (title.isEmpty() || street.isEmpty()) {
            out.put("reply", "Нужны название события и улица.");
            return out;
        }

        Optional<GeocodingService.Point> p = geo.find(street);
        if (p.isEmpty()) {
            out.put("reply", "Не нашёл адрес «" + street + "» во Владикавказе. Уточните улицу и номер дома.");
            return out;
        }

        Map<String, Object> event = new LinkedHashMap<>();
        event.put("title", title);
        event.put("description", args.path("description").asText(""));
        event.put("startTime", start.toString());
        event.put("endTime", args.hasNonNull("end_time") ? args.get("end_time").asText() : null);
        event.put("address", street);
        event.put("latitude", p.get().lat());
        event.put("longitude", p.get().lon());

        out.put("action", Map.of("type", "create_event", "event", event));
        out.put("reply", "Подготовил событие. Проверьте детали и подтвердите.");
        return out;
    }
}
