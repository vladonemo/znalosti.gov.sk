# znalosti.gov.sk

Central portal for machine-processable knowledge for Slovak public administration information systems. A semantic web (RDF/SPARQL) knowledge graph platform built with Spring Boot and Vaadin.

**License**: EUPL
**Authors**: Miroslav Líška, Marek Šurek
**Operated by**: Dátová kancelária MIRRI

## Tech Stack

- **Java 21** with **Spring Boot 3.5.9**
- **Vaadin 24.1.12** (server-side UI framework)
- **RDF4J 4.3.16** (semantic web / triple store)
- **Maven** build system
- **Docker** containerization with `docker-compose`
- **Eclipse Temurin JRE 21** runtime
- **IDSK Frontend 2.8.0** (Slovak Government Design System)

## Project Structure

```
src/main/java/sk/gov/knowledgegraph/
├── Application.java                 # Spring Boot entry point
├── DatabaseConfiguration.java       # RDF4J repository beans
├── RestConfigurator.java            # Jackson/REST configuration
├── RestExceptionHandler.java        # Global exception handling
├── controller/
│   ├── ResourceController.java      # Public REST API (/api/*)
│   └── integration/
│       ├── ReferenceIdentifierManagementController.java  # RefID API
│       └── SecurityConfig.java      # Spring Security config
├── model/
│   ├── RepositoryPool.java          # Multi-repo connection pool
│   ├── entity/                      # Dataset, Resource, Result
│   ├── exception/                   # ErrorCode, KnowledgeGraphException
│   └── refid/application/           # RefID domain model (7 application types)
├── service/
│   ├── SearchService.java           # Full-text search
│   ├── ResourceService.java         # RDF resource retrieval
│   ├── SparqlQueryService.java      # SPARQL query execution + HTML rendering
│   ├── DatasetService.java          # Dataset/ontology listing
│   ├── StatisticsService.java       # Graph statistics
│   ├── ReferenceIdentifierApplicationManagementService.java
│   └── query/                       # Query builder utilities
└── views/                           # Vaadin UI views (8 views)

src/main/java/sk/gov/idsk4j/        # IDSK government design components
frontend/styles/                     # CSS (IDSK, Lumo theme, view-specific)
src/main/resources/
├── application.yml                  # Spring profiles (default, test, prod)
└── META-INF/resources/
    ├── sourcedata/                  # RDF/OWL/Turtle source data
    ├── db/                          # Database initialization
    └── sparql/                      # SPARQL query templates
```

## Building

```bash
# Development
mvn clean install

# Production (builds Docker image)
mvn clean install -Pproduction

# Push Docker image to registry
mvn deploy -Pproduction
```

## Running Locally

```bash
# Start RDF4J server and proxy (from local-compose/)
cd local-compose && docker compose up -d

# Run the application in dev mode
mvn spring-boot:run

# Or with specific profile
mvn spring-boot:run -Dspring-boot.run.profiles=test-with-proxy
```

The application runs on `http://localhost:8080` by default.

## Docker Deployment

```bash
docker compose up -d
```

Services:
- **rdf-server** (port 8080) - RDF4J Workbench triple store
- **znalosti** (port 9090) - Production app (profile: prod)
- **znalosti-test** (port 9091) - Test app (profile: test)
- **znalosti-proxy** (port 81) - Reverse proxy

## API Endpoints

### Public API (`/api/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/resource?uri=` | Get RDF resource by URI (content-negotiated) |
| GET | `/api/search?q=` | Full-text search across knowledge graph |
| POST | `/api/sparql?q=` | Execute SPARQL queries (SELECT/CONSTRUCT/ASK) |
| GET | `/api/list-dbs` | List available databases |
| GET | `/api/export-db?db-id=` | Export entire database |
| GET | `/api/reload-dbs` | Reload all databases from GitHub |
| GET | `/api/reload-db/{branch-id}` | Reload specific branch |

### Integration API (`/integration/api/`) - Basic Auth protected
| Method | Endpoint | Description |
|--------|----------|-------------|
| CRUD | `/integration/api/refid/application` | Reference Identifier management |
| PUT | `.../application/apply` | Submit application (DRAFT→APPLIED) |
| PUT | `.../application/approve` | Approve application |
| PUT | `.../application/reject` | Reject application |
| GET | `.../application/search` | Search applications |

OpenAPI docs: `/integration/api/docs/swagger-ui/index.html`

## Spring Profiles

| Profile | DB URL | Repositories | Reset DB |
|---------|--------|--------------|----------|
| default | localhost:9090 | znalosti.gov.sk, refid | false |
| test-with-proxy | localhost:8080 | znalosti.gov.sk-test, refid-test | true |
| test | rdf-server:8080 | znalosti.gov.sk-test, refid-test | false |
| prod | rdf-server:8080 | znalosti.gov.sk, refid | false |

## Data Sources

RDF data is loaded from GitHub: `https://api.github.com/repos/slovak-egov/centralny-model-udajov`
Each branch creates a separate repository in RDF4J. Excluded branches: master, main, development, Refactoring, refid, refid-test.

## Conventions

- Language: Slovak (sk) for UI text and data labels
- RDF formats supported: JSON-LD, RDF/XML, Turtle, N-Triples
- SPARQL result formats: XML, CSV, TSV, JSON
- Content negotiation via `Accept` header
- Error responses use `ErrorCode` enum with detail maps
- Vaadin views use IDSK + GOV.UK CSS classes for government standard UI
- All REST endpoints support optional `db-id` parameter for multi-database queries
