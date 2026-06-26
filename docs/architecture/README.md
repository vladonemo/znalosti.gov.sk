# Architektonický UML model – znalosti.gov.sk

UML model architektúry aplikácie **znalosti.gov.sk** pre nástroj
**Sparx Enterprise Architect** (overené pre EA 16.1, build 1715, 64-bit).

## Súbory

| Súbor | Formát | Použitie |
|-------|--------|----------|
| `znalosti-gov-sk-architecture.xml` | UML 2.1 / XMI 2.1 | Importovateľný model. |
| `generate_ea_model.py` | Python generátor | Zdroj modelu; regeneruje XMI. |
| `generate_qea_from_base.py` | Python populátor | Naplní reálny EA base `.qea` modelom (viď „Možnosť A“). |

## Dva spôsoby, ako získať `.qea`

### Možnosť A – hotový `.qea` napĺňaním EA base (preferované)

`.qea` nie je možné vytvoriť úplne od nuly mimo EA – EA pri otváraní overuje
kompletnú verziovanú schému repozitára (chyby `Sparx Systems Database API
[0x00001086]`, resp. `Insert into usys_system () value ()`). Riešením je naplniť
**reálny prázdny EA base** modelom:

1. V EA vytvorte prázdny projekt: `Home` → **New Project** → uložte ako
   `docs/architecture/base.qea`. (Alebo skopírujte `EABase.qea` z inštalačného
   adresára EA – Sparx povoľuje jeho voľné kopírovanie.)
2. Tento `base.qea` sprístupnite (napr. commit do tejto vetvy).
3. Spustite populátor:
   ```bash
   cd docs/architecture
   python3 generate_qea_from_base.py base.qea znalosti-gov-sk-architecture.qea
   ```
   Skript načíta skutočnú schému base súboru a vloží celý model
   (balíky, triedy, atribúty, operácie, vzťahy, diagramy). Výsledný
   `znalosti-gov-sk-architecture.qea` sa otvára priamo cez **File → Open Project**.

### Možnosť B – import XMI do nového projektu

Nechajte EA vytvoriť prázdny `.qea` a naimportujte do neho model z XMI:

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
