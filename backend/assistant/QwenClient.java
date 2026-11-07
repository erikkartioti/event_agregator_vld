package com.eventagregatornew.eventagregatornew.assistant;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/** Клиент OpenAI-совместимого API Qwen (DashScope или локальный Ollama/vLLM). */
@Service
public class QwenClient {

    private static final String TOOLS = """
        [{"type":"function","function":{
          "name":"create_event",
          "description":"Подготовить создание события на карте по запросу пользователя.",
          "parameters":{"type":"object","properties":{
            "title":{"type":"string","description":"Название события"},
            "street":{"type":"string","description":"Улица и номер дома, без города"},
            "start_time":{"type":"string","description":"Начало, ISO-8601 без часового пояса, например 2026-11-14T19:00:00"},
            "end_time":{"type":"string","description":"Окончание, ISO-8601, если указано"},
            "description":{"type":"string","description":"Описание, если есть"}
          },"required":["title","street","start_time"]}}}]
        """;

    private final ObjectMapper mapper = new ObjectMapper();
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();

    @Value("${qwen.base-url}") private String baseUrl;
    @Value("${qwen.api-key:}") private String apiKey;
    @Value("${qwen.model}") private String model;

    public JsonNode complete(List<Map<String, String>> history) throws Exception {
        ZonedDateTime now = ZonedDateTime.now(ZoneId.of("Europe/Moscow"));
        String system = "Ты ассистент агрегатора событий Владикавказа. Сейчас "
            + now.format(DateTimeFormatter.ofPattern("EEEE, d MMMM yyyy, HH:mm", java.util.Locale.forLanguageTag("ru")))
            + " (Москва, UTC+3). Если пользователь просит создать событие, вызови create_event. "
            + "Относительные даты («в субботу», «завтра») переводи в точные от текущего момента. "
            + "Если не хватает названия, улицы или времени — задай один короткий уточняющий вопрос и не вызывай функцию. "
            + "Ничего не выдумывай.";

        ObjectNode body = mapper.createObjectNode();
        body.put("model", model);
        body.put("temperature", 0.1);
        ArrayNode msgs = body.putArray("messages");
        msgs.addObject().put("role", "system").put("content", system);
        for (Map<String, String> m : history) {
            String role = "assistant".equals(m.get("role")) ? "assistant" : "user"; // клиент не может подсунуть system
            msgs.addObject().put("role", role).put("content", m.getOrDefault("content", ""));
        }
        body.set("tools", mapper.readTree(TOOLS));

        HttpRequest req = HttpRequest.newBuilder(URI.create(baseUrl + "/chat/completions"))
            .timeout(Duration.ofSeconds(60))
            .header("Content-Type", "application/json")
            .header("Authorization", "Bearer " + apiKey)
            .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body)))
            .build();

        HttpResponse<String> res = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (res.statusCode() / 100 != 2) {
            throw new IllegalStateException("Qwen API " + res.statusCode() + ": " + res.body());
        }
        return mapper.readTree(res.body()).path("choices").path(0).path("message");
    }
}
