Start the application in development mode.

Prerequisites: RDF4J server must be running (use `cd local-compose && docker compose up -d` if needed).

Run: `mvn spring-boot:run`

The application will be available at http://localhost:8080.

For testing with proxy profile: `mvn spring-boot:run -Dspring-boot.run.profiles=test-with-proxy`