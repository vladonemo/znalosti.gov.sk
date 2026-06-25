# Architektonický UML model – znalosti.gov.sk

Tento priečinok obsahuje UML model architektúry aplikácie **znalosti.gov.sk**
určený pre nástroj **Sparx Enterprise Architect**.

## Súbory

| Súbor | Formát | Použitie |
|-------|--------|----------|
| `znalosti-gov-sk-architecture.qea` | Natívny EA projekt (SQLite) | Otvorte priamo: **File → Open Project** (Enterprise Architect 16+). |
| `znalosti-gov-sk-architecture.xml` | UML 2.1 / XMI 2.1 | Záložný, spoľahlivo importovateľný formát pre ľubovoľnú verziu EA. |
| `generate_ea_model.py` | Python generátor | Zdroj modelu; po zmene kódu regeneruje oba výstupy. |

### Otvorenie `.qea`
`.qea` je natívny formát projektu EA (SQLite databáza so schémou EA repozitára).
V Enterprise Architect zvoľte **File → Open Project** a vyberte súbor.

### Import `.xml` (XMI) – odporúčaný spoľahlivý postup
Ak by vaša verzia EA odmietla externe vytvorenú `.qea` databázu, vytvorte nový
prázdny projekt (**File → New Project**) a naimportujte model:
**Publish → Import Package from XMI** (resp. *Project → Import/Export → Import Package from XMI*),
vyberte `znalosti-gov-sk-architecture.xml`.

> Poznámka: súbory boli vygenerované mimo Enterprise Architect a v tomto
> prostredí ich nebolo možné otvoriť priamo v EA na overenie. `.qea` je platná
> SQLite databáza so schémou EA (`PRAGMA integrity_check = ok`), `.xml` je
> validný XMI 2.1. Pri akýchkoľvek problémoch s natívnym `.qea` použite import XMI.

## Štruktúra modelu

Model (root *znalosti.gov.sk*) je rozdelený do balíkov, každý s vlastným diagramom:

1. **01 Architecture Overview** – logický/komponentový pohľad na vrstvy a externé systémy.
2. **02 Presentation Layer (Vaadin UI)** – server-side UI (Vaadin Flow) a dizajn-systém IDSK (`idsk4j`):
   `MainView`, `SearchView`, `ResourceView`, `MetadataView`, `CategoriesView`,
   `DataView`, `SparqlView`, `ApiView`, `AboutView`, IDSK komponenty.
3. **03 REST API Layer** – `ResourceController` (`/api`), `ReferenceIdentifierManagementController` (`/integration/api/refid/application`).
4. **04 Service Layer** – `SearchService`, `ResourceService(2)`, `SparqlQueryService`,
   `StatisticsService`, `DatasetService`, `ReferenceIdentifierApplicationManagementService`,
   `LoadReferenceIdentifierApplicationManagementService`, `ApplicationURIMapperUtils`.
5. **05 Domain Model** – `RepositoryPool`, doménové entity (`AbstractEntity`, `Resource`,
   `Dataset`, `Result`) a hierarchia žiadostí refid
   (`SemanticResourceRegistrationApplication` a potomkovia, `User`, `Organization`,
   `ApplicationState`, komponenty ontológie atď.).
6. **06 Configuration & Infrastructure** – `Application`, `DatabaseConfiguration`,
   `SecurityConfig`, `RestConfigurator`, `RestExceptionHandler`.
7. **07 Deployment & External Systems** – nasadenie cez Docker Compose
   (`znalosti-proxy`, `znalosti`, `znalosti-test`, `rdf-server` / RDF4J) a externé
   systémy (GitHub *centralny-model-udajov*, MetaIS).

## Technologický kontext (odvodené zo zdrojového kódu)

- **Java 21**, **Spring Boot 3.5**, **Vaadin 24 (Flow)**, **Eclipse RDF4J 4.3**.
- Dátové úložisko: **RDF4J** triple store (SPARQL), repozitáre `znalosti.gov.sk` a `refid`.
- Zdrojové dáta sa načítavajú z **GitHub** vetiev repozitára `slovak-egov/centralny-model-udajov`.
- Integračné API chránené **HTTP Basic** (rola `INT_PARTNER`).

## Regenerácia

```bash
cd docs/architecture
python3 generate_ea_model.py
```

Generátor je jediný zdroj pravdy – po úprave architektúry upravte
`generate_ea_model.py` a spustite ho znova; prepíše `.qea` aj `.xml`.
