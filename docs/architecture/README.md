# Architektonický UML model – znalosti.gov.sk

UML model architektúry aplikácie **znalosti.gov.sk** pre nástroj
**Sparx Enterprise Architect** (overené pre EA 16.1, build 1715, 64-bit).

## Súbory

| Súbor | Formát | Použitie |
|-------|--------|----------|
| `znalosti-gov-sk-architecture.xml` | UML 2.1 / XMI 2.1 | Importovateľný model – z neho vznikne natívny `.qea` (viď nižšie). |
| `generate_ea_model.py` | Python generátor | Zdroj modelu; po zmene architektúry regeneruje XMI. |

## Ako získať funkčný `.qea` (dôležité)

`.qea` síce je SQLite databáza, ale Enterprise Architect pri otváraní
**overuje kompletnú, verziovanú schému EA repozitára** (~200 systémových tabuliek
a inicializačné dáta, ktoré sú dodávané iba v šablóne `EABase.qea` priamo v EA).
Súbor `.qea` vytvorený mimo EA preto **nie je možné otvoriť** – EA ho odmietne
chybou `Sparx Systems Database API [0x00001086]`.

Správny a podporovaný postup je nechať EA vytvoriť prázdny `.qea` a importovať
do neho tento model z XMI:

1. **Vytvorte nový projekt** – v EA: `Home` → **New Project** (alebo `Ctrl+N`).
   Zadajte názov a uložte ako napr. `znalosti-gov-sk-architecture.qea`.
   (EA tým naklonuje platnú šablónu `EABase.qea`.)
   Keď sa zobrazí *Model Wizard / Create from Pattern*, zatvorte ho – model
   naimportujeme v ďalšom kroku.
2. **Importujte XMI** – v okne *Browser* kliknite pravým tlačidlom na koreňový
   uzol **Model** (alebo na cieľový balík) →
   **Import/Export → Import Package from XMI…**
   (ekvivalent na páse s nástrojmi: `Publish` → *Model Exchange* →
   **Import Package from XMI**).
3. Vyberte súbor `znalosti-gov-sk-architecture.xml`, **zaškrtnite *Import Diagrams***
   a potvrďte **Import**.

Výsledkom je plnohodnotný `.qea` projekt s celým modelom vrátane diagramov,
ktorý sa už otvára priamo cez **File → Open Project**.

## Štruktúra modelu

Koreň *znalosti.gov.sk* je rozdelený do balíkov, každý s vlastným diagramom:

1. **01 Architecture Overview** – logický/komponentový pohľad na vrstvy a externé systémy.
2. **02 Presentation Layer (Vaadin UI)** – server-side UI (Vaadin Flow) a dizajn-systém IDSK (`idsk4j`):
   `MainView`, `SearchView`, `ResourceView`, `MetadataView`, `CategoriesView`,
   `DataView`, `SparqlView`, `ApiView`, `AboutView`.
3. **03 REST API Layer** – `ResourceController` (`/api`),
   `ReferenceIdentifierManagementController` (`/integration/api/refid/application`).
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

Po úprave architektúry upravte `generate_ea_model.py` a spustite ho znova –
prepíše `znalosti-gov-sk-architecture.xml`.
