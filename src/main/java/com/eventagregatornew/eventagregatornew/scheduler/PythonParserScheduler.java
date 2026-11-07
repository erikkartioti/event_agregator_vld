package com.eventagregatornew.eventagregatornew.scheduler;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "app.schedulers.enabled", havingValue = "true", matchIfMissing = true)
public class PythonParserScheduler {
    
    private static final Logger logger = LoggerFactory.getLogger(PythonParserScheduler.class);

    @Scheduled(cron = "0 08 16 * * *", zone = "Europe/Moscow")
    public void runPythonParsers() {
        try {
            // 1 parser - russian theater
            Process process1 = new ProcessBuilder("python", "A:/Agregator/event_agregator/event_agregator_new/parser-russiantheater.py").start();
            logParserOutput(process1, "Parser 1 - russian theater");

            // 2 parser - mariinsky
            Process process2 = new ProcessBuilder("python", "A:/Agregator/event_agregator/event_agregator_new/parser-mariinsky.py").start();
            logParserOutput(process2, "Parser 2 - mariinsky");

        } catch (IOException | InterruptedException e) {
            logger.error("Error executing the parsers: ", e);
        }
    }

    private void logParserOutput(Process process, String parserName) throws IOException, InterruptedException {
        // Capture the standard output (stdout) from the process
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        while ((line = reader.readLine()) != null) {
            logger.info(parserName + " Output: " + line);  // Log the standard output
        }

        // Capture the standard error (stderr) from the process
        BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        while ((line = errorReader.readLine()) != null) {
            logger.error(parserName + " Error: " + line);  // Log errors
        }

        // Wait for the process to finish and check its exit code
        int exitCode = process.waitFor();
        if (exitCode == 0) {
            logger.info(parserName + " executed successfully.");
        } else {
            logger.error(parserName + " failed with exit code " + exitCode);
        }
    }
}
