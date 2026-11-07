package com.eventagregatornew.eventagregatornew.assistant;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Optional;

/** Адрес -> координаты через Nominatim, ограничено рамкой Владикавказа. */
@Service
public class GeocodingService {

    public record Point(double lat, double lon, String displayName) {}

    private final ObjectMapper mapper = new ObjectMapper();
    private final HttpClient http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();

    public Optional<Point> find(String street) throws Exception {
        String q = URLEncoder.encode(street + ", Владикавказ", StandardCharsets.UTF_8);
        URI uri = URI.create("https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&accept-language=ru"
            + "&viewbox=44.45,43.15,44.90,42.90&bounded=1&q=" + q);
        HttpRequest req = HttpRequest.newBuilder(uri)
            .timeout(Duration.ofSeconds(15))
            .header("User-Agent", "event-agregator-vld/1.0 (contact: set-your-email)") // требование политики Nominatim
            .build();
        HttpResponse<String> res = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (res.statusCode() != 200) return Optional.empty();
        JsonNode arr = mapper.readTree(res.body());
        if (!arr.isArray() || arr.isEmpty()) return Optional.empty();
        JsonNode f = arr.get(0);
        return Optional.of(new Point(f.path("lat").asDouble(), f.path("lon").asDouble(), f.path("display_name").asText()));
    }
}
