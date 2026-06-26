#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator of the UML architecture model for the application znalosti.gov.sk.

Produces two artifacts in this directory:

  * znalosti-gov-sk-architecture.qea  - native Enterprise Architect project
                                        (SQLite database following the EA
                                        repository schema). Open directly with
                                        File > Open Project in Enterprise
                                        Architect 16+.
  * znalosti-gov-sk-architecture.xml  - UML 2.1 / XMI 2.1 export. Use this as a
                                        guaranteed-importable fallback
                                        (Publish > Import Package from XMI) in
                                        any Enterprise Architect version.

The model content is derived from the source code of the repository
(Spring Boot 3.5 + Vaadin 24 + Eclipse RDF4J knowledge-graph portal).
"""

import os
import sqlite3
import uuid
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
QEA_PATH = os.path.join(HERE, "znalosti-gov-sk-architecture.qea")
XMI_PATH = os.path.join(HERE, "znalosti-gov-sk-architecture.xml")

NOW = "2026-06-25 00:00:00"


def guid():
    return "{" + str(uuid.uuid4()).upper() + "}"


# ---------------------------------------------------------------------------
#  In-memory model definition
# ---------------------------------------------------------------------------
# Every package / element / connector / diagram is captured in plain Python
# structures first, then emitted to both the EA SQLite schema and to XMI.

class Model:
    def __init__(self):
        self.packages = []      # dict: id, name, parent_id, guid, notes
        self.elements = []      # dict: id, name, type, stereotype, package_id, guid, notes, attrs[], ops[], abstract
        self.connectors = []    # dict: id, type, name, src, dst, stereotype, notes, src_card, dst_card
        self.diagrams = []      # dict: id, name, package_id, type, guid, notes, elems[], links[]
        self._pid = 0
        self._eid = 0
        self._cid = 0
        self._did = 0

    def pkg(self, name, parent_id, notes=""):
        self._pid += 1
        p = dict(id=self._pid, name=name, parent_id=parent_id, guid=guid(), notes=notes)
        self.packages.append(p)
        return self._pid

    def elem(self, name, package_id, etype="Class", stereotype="", notes="",
             attrs=None, ops=None, abstract=False):
        self._eid += 1
        e = dict(id=self._eid, name=name, type=etype, stereotype=stereotype,
                 package_id=package_id, guid=guid(), notes=notes,
                 attrs=attrs or [], ops=ops or [], abstract=abstract)
        self.elements.append(e)
        return self._eid

    def conn(self, ctype, src, dst, name="", stereotype="", notes="",
             src_card="", dst_card=""):
        self._cid += 1
        c = dict(id=self._cid, type=ctype, name=name, src=src, dst=dst,
                 stereotype=stereotype, guid=guid(), notes=notes,
                 src_card=src_card, dst_card=dst_card)
        self.connectors.append(c)
        return self._cid

    def diagram(self, name, package_id, dtype, notes="", elems=None, links=None):
        self._did += 1
        d = dict(id=self._did, name=name, package_id=package_id, type=dtype,
                 guid=guid(), notes=notes, elems=elems or [], links=links or [])
        self.diagrams.append(d)
        return self._did


m = Model()

# --- Packages -------------------------------------------------------------
ROOT = m.pkg("znalosti.gov.sk", 0,
             "Centralny portal strojovo-spracovatelnych znalosti pre informacne "
             "systemy verejnej spravy. Spring Boot 3.5 + Vaadin 24 (Flow) + "
             "Eclipse RDF4J. Architektonicky model aplikacie.")
P_OVERVIEW = m.pkg("01 Architecture Overview", ROOT,
                   "Logicky pohlad na vrstvy aplikacie a externe systemy.")
P_UI = m.pkg("02 Presentation Layer (Vaadin UI)", ROOT,
             "Server-side UI postavene na Vaadin Flow a dizajn-systeme IDSK (idsk4j).")
P_REST = m.pkg("03 REST API Layer", ROOT,
               "Spring MVC REST kontrolery - verejne API a integracne rozhranie.")
P_SVC = m.pkg("04 Service Layer", ROOT,
              "Aplikacne sluzby - vyhladavanie, SPARQL, statistiky, sprava ziadosti refid.")
P_DOM = m.pkg("05 Domain Model", ROOT,
              "Domenove entity, model ziadosti o registraciu (refid) a pristup k RDF uloziskam.")
P_CFG = m.pkg("06 Configuration & Infrastructure", ROOT,
              "Spring konfiguracia, bezpecnost a bootstrap aplikacie.")
P_DEP = m.pkg("07 Deployment & External Systems", ROOT,
              "Nasadenie (Docker Compose) a externe systemy.")

# --- 02 Presentation Layer ------------------------------------------------
main_view = m.elem("MainView", P_UI, stereotype="Vaadin View",
                   notes="AppLayout - hlavna sablona, navigacny IDSK header s polozkami "
                         "Vyhladavanie, Ontologie, Kategorie, Priklady dat, SPARQL, API, O portali.")
search_view = m.elem("SearchView", P_UI, stereotype="Vaadin View",
                     notes="Fulltextove vyhladavanie nad znalostnym grafom (3 urovne).")
resource_view = m.elem("ResourceView", P_UI, stereotype="Vaadin View",
                       notes="Detail RDF zdroja (subject/predicate/object), priame a inverzne vazby.")
metadata_view = m.elem("MetadataView", P_UI, stereotype="Vaadin View", notes="Prehlad ontologii.")
categories_view = m.elem("CategoriesView", P_UI, stereotype="Vaadin View", notes="Kategorie / temy.")
data_view = m.elem("DataView", P_UI, stereotype="Vaadin View", notes="Priklady datovych sad.")
sparql_view = m.elem("SparqlView", P_UI, stereotype="Vaadin View", notes="Interaktivny SPARQL endpoint UI.")
api_view = m.elem("ApiView", P_UI, stereotype="Vaadin View", notes="Dokumentacia REST API.")
about_view = m.elem("AboutView", P_UI, stereotype="Vaadin View", notes="O portali.")

idsk_header = m.elem("IDSKHeaderWeb", P_UI, stereotype="UI Component", notes="IDSK dizajn-system header.")
idsk_header_main = m.elem("IDSKHeaderWebMain", P_UI, stereotype="UI Component")
idsk_header_nav = m.elem("IDSKHeaderWebNav", P_UI, stereotype="UI Component")
idsk_results = m.elem("IDSKSearchResultsContent", P_UI, stereotype="UI Component")
idsk_filter = m.elem("IDSKSearchResultsFilter", P_UI, stereotype="UI Component")

ALL_VIEWS = [search_view, resource_view, metadata_view, categories_view,
             data_view, sparql_view, api_view, about_view]

# --- 03 REST API Layer ----------------------------------------------------
resource_ctrl = m.elem(
    "ResourceController", P_REST, stereotype="RestController",
    notes="@RequestMapping('/api') - verejne REST API znalostneho grafu.",
    ops=[("resource", "StreamingResponseBody", "GET/POST /api/resource"),
         ("search", "List<Result>", "GET /api/search"),
         ("listDbs", "List<String>", "GET /api/list-dbs"),
         ("reloadDbs", "Set<String>", "GET /api/reload-dbs"),
         ("exportDb", "StreamingResponseBody", "GET /api/export-db"),
         ("reloadDbByBranchId", "Set<String>", "GET /api/reload-db/{branch-id}"),
         ("sparqlPostURLencoded", "StreamingResponseBody", "POST /api/sparql")])
refid_ctrl = m.elem(
    "ReferenceIdentifierManagementController", P_REST, stereotype="RestController",
    notes="@RequestMapping('/integration/api/refid/application') - integracne rozhranie "
          "na spravu referencovatelnych identifikatorov (chranene HTTP Basic, rola INT_PARTNER).",
    ops=[("getApplication", "SemanticResourceRegistrationApplication", "GET"),
         ("createApplication", "SemanticResourceRegistrationApplication", "POST"),
         ("updateDraftApplication", "SemanticResourceRegistrationApplication", "PUT"),
         ("deleteApplication", "void", "DELETE"),
         ("applyApplication", "SemanticResourceRegistrationApplication", "PUT /apply"),
         ("rejectApplication", "SemanticResourceRegistrationApplication", "PUT /reject"),
         ("approveApplication", "SemanticResourceRegistrationApplication", "PUT /approve"),
         ("resetDb", "void", "DELETE /reset-db"),
         ("search", "SearchResult", "GET /search")])

# --- 04 Service Layer -----------------------------------------------------
search_svc = m.elem("SearchService", P_SVC, stereotype="Service",
                    notes="Fulltextove SPARQL vyhladavanie nad RDF grafmi.",
                    ops=[("search", "List<Result>", "(searchString, dbId)")])
resource_svc = m.elem("ResourceService", P_SVC, stereotype="Service",
                      ops=[("describeUriBySelect", "List<Resource>", ""),
                           ("getBaseProperties", "Resource", "")])
resource_svc2 = m.elem("ResourceService2", P_SVC, stereotype="Service")
sparql_svc = m.elem("SparqlQueryService", P_SVC, stereotype="Service",
                    ops=[("getTupleQueryResultHtml", "String", ""),
                         ("getGraphQueryResultHtml", "String", ""),
                         ("getBooleanQueryResultHtml", "String", "")])
stats_svc = m.elem("StatisticsService", P_SVC, stereotype="Service",
                   ops=[("getAllTriplesCount", "int", ""),
                        ("getAllNamedGraphsCount", "int", ""),
                        ("getDatasetsCount", "int", ""),
                        ("getCatalogsCount", "int", "")])
dataset_svc = m.elem("DatasetService", P_SVC, stereotype="Service",
                     ops=[("listData", "List<Dataset>", "")])
refid_svc = m.elem("ReferenceIdentifierApplicationManagementService", P_SVC, stereotype="Service",
                   notes="Sprava zivotneho cyklu ziadosti refid (DRAFT->APPLIED->APPROVED/REJECTED).",
                   ops=[("createApplication", "...", ""), ("updateDraftApplication", "...", ""),
                        ("deleteApplication", "void", ""), ("applyApplication", "...", ""),
                        ("rejectApplication", "...", ""), ("approveApplication", "...", ""),
                        ("search", "SearchResult", ""), ("resetDb", "void", ""),
                        ("validate", "void", "")])
load_refid_svc = m.elem("LoadReferenceIdentifierApplicationManagementService", P_SVC, stereotype="Service",
                        ops=[("loadApplicationFromDB", "SemanticResourceRegistrationApplication", "")])
uri_mapper = m.elem("ApplicationURIMapperUtils", P_SVC, stereotype="utility",
                    notes="Mapovanie domenoveho objektu ziadosti na/z RDF statements.")

# --- 05 Domain Model ------------------------------------------------------
repo_pool = m.elem(
    "RepositoryPool", P_DOM, stereotype="repository",
    notes="Pool pripojeni k RDF4J uloziskam. Nacitava data z GitHub vetiev "
          "(centralny-model-udajov) a spravuje pomenovane RDF repozitare.",
    attrs=[("defaultRepositoryId", "String"), ("dbUrl", "String"),
           ("githubRepositoryUrl", "String"), ("repositories", "Map<String,Repository>")],
    ops=[("getDefaultRepository", "Repository", ""),
         ("getRepositoryOrDefault", "Repository", ""),
         ("reloadDbFromBranch", "Set<String>", ""),
         ("exportDb", "void", ""), ("createRepository", "Repository", "")])

abstract_entity = m.elem("AbstractEntity", P_DOM, abstract=True,
                         notes="Spolocny predok domenovych entit.")
result = m.elem("Result", P_DOM,
                attrs=[("subject", "String"), ("predicate/property", "String"),
                       ("object", "String"), ("graph", "String"),
                       ("graphName", "String"), ("searchString", "String")],
                notes="Vysledok vyhladavania.")
resource_ent = m.elem("Resource", P_DOM,
                      attrs=[("uri", "String"), ("prefLabel", "String"), ("type", "String"),
                             ("subject", "String"), ("predicate", "String"), ("object", "String"),
                             ("isInverse", "String"), ("graph", "String"), ("language", "String")],
                      notes="RDF zdroj a jeho vlastnosti (so skracovanim URI na prefixy).")
dataset_ent = m.elem("Dataset", P_DOM,
                     attrs=[("dataset", "String"), ("datasetTitle", "String"),
                            ("publisher", "String"), ("publisherName", "String"),
                            ("catalog", "String"), ("theme", "String"), ("version", "String")],
                     notes="DCAT datova sada.")

# refid application hierarchy
srra = m.elem(
    "SemanticResourceRegistrationApplication", P_DOM, abstract=True, stereotype="abstract",
    notes="Abstraktna ziadost o registraciu semantickeho datoveho prvku.",
    attrs=[("uri", "String"), ("description", "String"), ("createdAt", "LocalDate"),
           ("lastModifiedAt", "LocalDate"), ("appliedAt", "LocalDate"),
           ("rejectedAt", "LocalDate"), ("approvedAt", "LocalDate"),
           ("state", "ApplicationState"), ("applicant", "Organization"),
           ("createdBy", "User"), ("approvedBy", "User")])
ontology_app = m.elem("OntologyRegistrationApplication", P_DOM, notes="Ziadost o registraciu ontologie.",
                      attrs=[("subject", "OntologyConcept")])
ontology_ver_app = m.elem("OntologyVersionRegistrationApplication", P_DOM,
                          notes="Ziadost o registraciu verzie ontologie.")
ontology_comp_app = m.elem("OntologyComponentRegistrationApplication<T>", P_DOM, abstract=True,
                           notes="Ziadost o registraciu ontologickeho prvku.",
                           attrs=[("subject", "T extends OntologyComponent")])
class_comp_app = m.elem("ClassComponentRegistrationApplication", P_DOM)
dt_prop_app = m.elem("DatatypePropertyComponentRegistrationApplication", P_DOM)
obj_prop_app = m.elem("ObjectPropertyComponentRegistrationApplication", P_DOM)
uri_tpl_app = m.elem("URITemplateRegistrationApplication", P_DOM)

user = m.elem("User", P_DOM, attrs=[("username", "String"), ("institutionId", "String")])
organization = m.elem("Organization", P_DOM, attrs=[("organizationId", "String"), ("uri", "String")])
app_state = m.elem("ApplicationState", P_DOM, etype="Enumeration", stereotype="enumeration",
                   attrs=[("DRAFT", ""), ("APPLIED", ""), ("APPROVED", ""), ("REJECTED", "")])
value_type = m.elem("ValueType", P_DOM, etype="Enumeration", stereotype="enumeration")
ontology = m.elem("Ontology", P_DOM)
ontology_concept = m.elem("OntologyConcept", P_DOM)
uri_template = m.elem("URITemplate", P_DOM)
uri_tpl_param = m.elem("URITemplateQueryParam", P_DOM)

ont_component = m.elem("OntologyComponent", P_DOM, abstract=True)
class_component = m.elem("ClassComponent", P_DOM)
dt_component = m.elem("DatatypePropertyComponent", P_DOM)
obj_component = m.elem("ObjectPropertyComponent", P_DOM)

kg_exception = m.elem("KnowledgeGraphException", P_DOM, stereotype="exception")
error_code = m.elem("ErrorCode", P_DOM, etype="Enumeration", stereotype="enumeration")
github_branch = m.elem("GithubBranch", P_DOM, notes="DTO pre GitHub API vetvy.")

# --- 06 Configuration & Infrastructure ------------------------------------
application = m.elem("Application", P_CFG, stereotype="Spring Boot Application",
                     notes="@SpringBootApplication - vstupny bod aplikacie.")
db_config = m.elem("DatabaseConfiguration", P_CFG, stereotype="Configuration",
                   notes="@Configuration - definuje beans znalostiRepository (RepositoryPool) "
                         "a refidRepository (RDF4J Repository).",
                   ops=[("getZnalostiRepository", "RepositoryPool", "@Bean"),
                        ("getRefIdRepository", "Repository", "@Bean")])
security_config = m.elem("SecurityConfig", P_CFG, stereotype="Configuration",
                         notes="Spring Security - HTTP Basic, /integration/** vyzaduje rolu INT_PARTNER, "
                               "BCrypt, in-memory pouzivatel (metais).")
rest_configurator = m.elem("RestConfigurator", P_CFG, stereotype="Configuration")
rest_exc_handler = m.elem("RestExceptionHandler", P_CFG, stereotype="ControllerAdvice")

# --- 07 Deployment & External Systems -------------------------------------
node_proxy = m.elem("znalosti-proxy", P_DEP, etype="Node", stereotype="device",
                    notes="Reverzny proxy (znalosti-proxy image). Port 81 -> 80.")
node_app_prod = m.elem("znalosti", P_DEP, etype="Node", stereotype="device",
                       notes="Spring Boot aplikacia, profil 'prod'. Port 9090 -> 8080.")
node_app_test = m.elem("znalosti-test", P_DEP, etype="Node", stereotype="device",
                       notes="Spring Boot aplikacia, profil 'test'. Port 9091 -> 8080.")
node_rdf = m.elem("rdf-server", P_DEP, etype="Node", stereotype="device",
                  notes="Eclipse RDF4J Workbench 4.3.8 (Tomcat). Port 8080. "
                        "Repozitare: znalosti.gov.sk, refid (NativeStore spoc,posc).")
artifact_jar = m.elem("znalosti.jar", P_DEP, etype="Artifact", stereotype="jar",
                      notes="Spustitelny Spring Boot JAR (Vaadin frontend zabundlovany).")
node_browser = m.elem("Web Browser", P_DEP, etype="Node", stereotype="device",
                      notes="Klient - pouzivatel portalu.")
ext_github = m.elem("GitHub: centralny-model-udajov", P_DEP, etype="Node", stereotype="external system",
                    notes="Zdrojove RDF data (vetvy repozitara). REST: api.github.com/repos/slovak-egov/centralny-model-udajov.")
ext_metais = m.elem("MetaIS (Integration Partner)", P_DEP, etype="Node", stereotype="external system",
                    notes="Centralny metainformacny system VS - integracny partner refid API.")

# --- 01 Architecture Overview (logical components) ------------------------
c_ui = m.elem("Web UI (Vaadin Flow + IDSK)", P_OVERVIEW, etype="Component", stereotype="subsystem",
              notes="Prezentacna vrstva - server-side UI.")
c_rest = m.elem("REST API", P_OVERVIEW, etype="Component", stereotype="subsystem",
                notes="Verejne API (/api) a integracne API (/integration).")
c_svc = m.elem("Service Layer", P_OVERVIEW, etype="Component", stereotype="subsystem",
               notes="Aplikacna logika.")
c_repo = m.elem("RDF Repository Access (RepositoryPool)", P_OVERVIEW, etype="Component", stereotype="subsystem",
                notes="Pristup k RDF4J, nacitanie dat z GitHub.")
c_sec = m.elem("Security (Spring Security)", P_OVERVIEW, etype="Component", stereotype="subsystem")
c_rdf4j = m.elem("RDF4J Triple Store", P_OVERVIEW, etype="Component", stereotype="external system")
c_github = m.elem("GitHub Source Data", P_OVERVIEW, etype="Component", stereotype="external system")
c_metais = m.elem("MetaIS", P_OVERVIEW, etype="Component", stereotype="external system")

# ---------------------------------------------------------------------------
#  Connectors
# ---------------------------------------------------------------------------
DEP = "Dependency"
GEN = "Generalization"
ASSOC = "Association"
USE = "Usage"
DEPLOY = "Deploy"
MANIFEST = "Manifest"

# Overview component wiring
m.conn(USE, c_ui, c_rest, notes="HTTP")
m.conn(USE, c_ui, c_svc)
m.conn(USE, c_rest, c_svc)
m.conn(USE, c_svc, c_repo)
m.conn(USE, c_rest, c_sec)
m.conn(USE, c_repo, c_rdf4j, name="SPARQL / RDF4J REST")
m.conn(USE, c_repo, c_github, name="HTTPS (zipball/branches)")
m.conn(USE, c_metais, c_rest, name="refid integration API")

# UI -> idsk
m.conn(ASSOC, main_view, idsk_header)
m.conn(ASSOC, idsk_header, idsk_header_main)
m.conn(ASSOC, idsk_header, idsk_header_nav)
# views use services
m.conn(DEP, search_view, search_svc)
m.conn(DEP, resource_view, resource_svc)
m.conn(DEP, data_view, dataset_svc)
m.conn(DEP, sparql_view, sparql_svc)
m.conn(DEP, metadata_view, stats_svc)

# controllers -> services
m.conn(DEP, resource_ctrl, search_svc)
m.conn(DEP, resource_ctrl, repo_pool)
m.conn(DEP, refid_ctrl, refid_svc)

# services -> domain / repo
m.conn(DEP, search_svc, repo_pool)
m.conn(DEP, resource_svc, repo_pool)
m.conn(DEP, sparql_svc, repo_pool)
m.conn(DEP, stats_svc, repo_pool)
m.conn(DEP, dataset_svc, repo_pool)
m.conn(DEP, refid_svc, load_refid_svc)
m.conn(DEP, refid_svc, uri_mapper)
m.conn(DEP, search_svc, result)
m.conn(DEP, resource_svc, resource_ent)
m.conn(DEP, dataset_svc, dataset_ent)

# domain generalizations
m.conn(GEN, resource_ent, abstract_entity)
m.conn(GEN, dataset_ent, abstract_entity)
m.conn(GEN, ontology_app, srra)
m.conn(GEN, ontology_ver_app, srra)
m.conn(GEN, ontology_comp_app, srra)
m.conn(GEN, class_comp_app, ontology_comp_app)
m.conn(GEN, dt_prop_app, ontology_comp_app)
m.conn(GEN, obj_prop_app, ontology_comp_app)
m.conn(GEN, uri_tpl_app, srra)
m.conn(GEN, class_component, ont_component)
m.conn(GEN, dt_component, ont_component)
m.conn(GEN, obj_component, ont_component)

# domain associations
m.conn(ASSOC, srra, user, name="createdBy/approvedBy", dst_card="0..*")
m.conn(ASSOC, srra, organization, name="applicant", dst_card="1")
m.conn(ASSOC, srra, app_state, name="state", dst_card="1")
m.conn(ASSOC, ontology_app, ontology_concept, name="subject")
m.conn(ASSOC, ontology_comp_app, ont_component, name="subject")
m.conn(ASSOC, class_comp_app, class_component, name="subject")
m.conn(ASSOC, dt_prop_app, dt_component, name="subject")
m.conn(ASSOC, obj_prop_app, obj_component, name="subject")
m.conn(ASSOC, uri_tpl_app, uri_template, name="subject")
m.conn(ASSOC, uri_template, uri_tpl_param, dst_card="0..*")
m.conn(ASSOC, ontology_concept, ontology, name="ontology")

# config
m.conn(DEP, db_config, repo_pool, name="@Bean znalostiRepository")
m.conn(DEP, refid_svc, db_config, name="refidRepository")
m.conn(DEP, application, db_config)
m.conn(DEP, refid_ctrl, security_config, name="secured by")

# deployment
m.conn(DEPLOY, artifact_jar, node_app_prod)
m.conn(DEPLOY, artifact_jar, node_app_test)
m.conn(MANIFEST, artifact_jar, c_ui)
m.conn(ASSOC, node_browser, node_proxy, name="HTTPS")
m.conn(ASSOC, node_proxy, node_app_prod, name="HTTP :9090")
m.conn(ASSOC, node_proxy, node_app_test, name="HTTP :9091")
m.conn(ASSOC, node_app_prod, node_rdf, name="RDF4J REST :8080")
m.conn(ASSOC, node_app_test, node_rdf, name="RDF4J REST :8080")
m.conn(ASSOC, node_app_prod, ext_github, name="HTTPS source data")
m.conn(ASSOC, ext_metais, node_proxy, name="refid integration API")

# ---------------------------------------------------------------------------
#  Diagrams
# ---------------------------------------------------------------------------
m.diagram("01 Architecture Overview", P_OVERVIEW, "Logical",
          notes="Vrstvovy / komponentovy pohlad na aplikaciu a externe systemy.",
          elems=[c_ui, c_rest, c_svc, c_repo, c_sec, c_rdf4j, c_github, c_metais])
m.diagram("02 Presentation Layer", P_UI, "Logical",
          elems=[main_view] + ALL_VIEWS + [idsk_header, idsk_header_main, idsk_header_nav,
                                           idsk_results, idsk_filter,
                                           search_svc, resource_svc, dataset_svc, sparql_svc, stats_svc])
m.diagram("03 REST API Layer", P_REST, "Logical",
          elems=[resource_ctrl, refid_ctrl, search_svc, repo_pool, refid_svc, security_config])
m.diagram("04 Service Layer", P_SVC, "Logical",
          elems=[search_svc, resource_svc, resource_svc2, sparql_svc, stats_svc, dataset_svc,
                 refid_svc, load_refid_svc, uri_mapper, repo_pool])
m.diagram("05a Domain Model - refid Applications", P_DOM, "Logical",
          notes="Hierarchia ziadosti o registraciu referencovatelnych identifikatorov.",
          elems=[srra, ontology_app, ontology_ver_app, ontology_comp_app, class_comp_app,
                 dt_prop_app, obj_prop_app, uri_tpl_app, user, organization, app_state,
                 ontology_concept, ont_component, class_component, dt_component, obj_component,
                 uri_template, uri_tpl_param, ontology])
m.diagram("05b Domain Model - Core Entities", P_DOM, "Logical",
          elems=[abstract_entity, resource_ent, dataset_ent, result, repo_pool,
                 kg_exception, error_code, github_branch])
m.diagram("06 Configuration & Infrastructure", P_CFG, "Logical",
          elems=[application, db_config, security_config, rest_configurator, rest_exc_handler, repo_pool])
m.diagram("07 Deployment", P_DEP, "Deployment",
          notes="Nasadenie cez Docker Compose.",
          elems=[node_browser, node_proxy, node_app_prod, node_app_test, node_rdf,
                 artifact_jar, ext_github, ext_metais])


# ===========================================================================
#  EA SQLite (.qea) emitter
# ===========================================================================
def emit_qea(model, path):
    if os.path.exists(path):
        os.remove(path)
    db = sqlite3.connect(path)
    cur = db.cursor()

    # --- EA repository schema (core + reference tables) -------------------
    cur.executescript("""
    CREATE TABLE t_package (
        Package_ID INTEGER PRIMARY KEY, Name TEXT, Parent_ID INTEGER,
        CreatedDate TEXT, ModifiedDate TEXT, Notes TEXT, ea_guid TEXT,
        XMLPath TEXT, IsControlled INTEGER, LastLoadDate TEXT, LastSaveDate TEXT,
        Version TEXT, Protected INTEGER, PkgOwner TEXT, IsNamespace INTEGER,
        TPos INTEGER, PackageFlags TEXT, BatchSave INTEGER, BatchLoad INTEGER,
        UseDTD INTEGER, LogXML INTEGER, CodePath TEXT, Namespace TEXT,
        UMLVersion TEXT, UseModelGen INTEGER, GenFile TEXT, GenOptions TEXT);

    CREATE TABLE t_object (
        Object_ID INTEGER PRIMARY KEY, Object_Type TEXT, Diagram_ID INTEGER,
        Name TEXT, Alias TEXT, Author TEXT, Version TEXT, Note TEXT,
        Package_ID INTEGER, Stereotype TEXT, Complexity TEXT, Effort TEXT,
        Style TEXT, Backcolor INTEGER, BorderStyle INTEGER, BorderWidth INTEGER,
        Fontcolor INTEGER, Bordercolor INTEGER, CreatedDate TEXT, ModifiedDate TEXT,
        Status TEXT, Abstract TEXT, IsSpec TEXT, Scope TEXT, GenType TEXT,
        GenFile TEXT, Header1 TEXT, Header2 TEXT, PDATA1 TEXT, PDATA2 TEXT,
        PDATA3 TEXT, PDATA4 TEXT, PDATA5 TEXT, Phase TEXT, ea_guid TEXT,
        ParentID INTEGER, Classifier INTEGER, Classifier_guid TEXT,
        Multiplicity TEXT, NType INTEGER, Persistence TEXT, Cardinality TEXT,
        Concurrency TEXT, Visibility TEXT, GenLinks TEXT, TPos INTEGER,
        IsRoot TEXT, IsLeaf TEXT, IsActive TEXT);

    CREATE TABLE t_attribute (
        Object_ID INTEGER, Name TEXT, Scope TEXT, Stereotype TEXT, Containment TEXT,
        IsStatic INTEGER, IsCollection INTEGER, IsOrdered INTEGER, AllowDuplicates INTEGER,
        LowerBound TEXT, UpperBound TEXT, Container TEXT, Notes TEXT, Derived INTEGER,
        ID INTEGER PRIMARY KEY, Pos INTEGER, GenOption TEXT, Length TEXT, Precision TEXT,
        Scale TEXT, Const INTEGER, Style TEXT, Classifier TEXT, [Default] TEXT,
        Type TEXT, ea_guid TEXT, StyleEx TEXT, Object_Type TEXT);

    CREATE TABLE t_operation (
        OperationID INTEGER PRIMARY KEY, Object_ID INTEGER, Name TEXT, Scope TEXT,
        Type TEXT, ReturnArray INTEGER, IsStatic INTEGER, IsAbstract INTEGER,
        Concurrency TEXT, Notes TEXT, Stereotype TEXT, Pure INTEGER, Pos INTEGER,
        IsQuery INTEGER, IsConst INTEGER, IsSynchronized INTEGER, GenOption TEXT,
        ea_guid TEXT, StyleEx TEXT, Classifier TEXT, Code TEXT, Behaviour TEXT);

    CREATE TABLE t_connector (
        Connector_ID INTEGER PRIMARY KEY, Name TEXT, Direction TEXT, Notes TEXT,
        Connector_Type TEXT, SubType TEXT, SourceCard TEXT, SourceAccess TEXT,
        SourceElement TEXT, DestCard TEXT, DestAccess TEXT, DestElement TEXT,
        SourceRole TEXT, SourceRoleType TEXT, SourceRoleNote TEXT, SourceContainment TEXT,
        SourceIsAggregate INTEGER, SourceIsOrdered INTEGER, SourceQualifier TEXT,
        DestRole TEXT, DestRoleType TEXT, DestRoleNote TEXT, DestContainment TEXT,
        DestIsAggregate INTEGER, DestIsOrdered INTEGER, DestQualifier TEXT,
        Start_Object_ID INTEGER, End_Object_ID INTEGER, Start_Edge INTEGER,
        End_Edge INTEGER, PtStartX INTEGER, PtStartY INTEGER, PtEndX INTEGER,
        PtEndY INTEGER, SeqNo INTEGER, HeadStyle INTEGER, LineStyle INTEGER,
        RouteStyle INTEGER, IsBold INTEGER, LineColor INTEGER, Stereotype TEXT,
        VirtualInheritance TEXT, LinkAccess TEXT, ea_guid TEXT, IsRoot TEXT,
        IsLeaf TEXT, IsSpec TEXT, SourceChangeable TEXT, DestChangeable TEXT,
        SourceTS TEXT, DestTS TEXT, StateFlags TEXT, ActionFlags TEXT,
        IsSignal INTEGER, IsStimulus INTEGER, DispatchAction TEXT, Target2 INTEGER,
        StyleEx TEXT, SourceStyle TEXT, DestStyle TEXT, EventFlags TEXT, PDATA1 TEXT,
        PDATA2 TEXT, PDATA3 TEXT, PDATA4 TEXT, PDATA5 TEXT);

    CREATE TABLE t_diagram (
        Diagram_ID INTEGER PRIMARY KEY, Package_ID INTEGER, ParentID INTEGER,
        Diagram_Type TEXT, Name TEXT, Version TEXT, Author TEXT, ShowDetails INTEGER,
        Notes TEXT, Stereotype TEXT, AttPub INTEGER, AttPri INTEGER, AttPro INTEGER,
        Orientation TEXT, cx INTEGER, cy INTEGER, Scale INTEGER, CreatedDate TEXT,
        ModifiedDate TEXT, HTMLPath TEXT, ShowForeign INTEGER, ShowBorder INTEGER,
        ShowPackageContents INTEGER, PDATA TEXT, Locked INTEGER, ea_guid TEXT,
        TPos INTEGER, SwimlaneDef TEXT, StyleEx TEXT);

    CREATE TABLE t_diagramobjects (
        Diagram_ID INTEGER, Object_ID INTEGER, RectTop INTEGER, RectLeft INTEGER,
        RectRight INTEGER, RectBottom INTEGER, Sequence INTEGER, ObjectStyle TEXT,
        Instance_ID INTEGER PRIMARY KEY);

    CREATE TABLE t_diagramlinks (
        DiagramID INTEGER, ConnectorID INTEGER, Geometry TEXT, Style TEXT,
        Hidden INTEGER, Path TEXT, Instance_ID INTEGER PRIMARY KEY);

    CREATE TABLE t_xref (
        XrefID TEXT PRIMARY KEY, Name TEXT, Type TEXT, Visibility TEXT,
        Namespace TEXT, Requirement TEXT, [Constraint] TEXT, Behavior TEXT,
        Partition TEXT, Description TEXT, Client TEXT, Supplier TEXT, Link TEXT);

    CREATE TABLE t_objectproperties (
        PropertyID INTEGER PRIMARY KEY, Object_ID INTEGER, Property TEXT,
        Value TEXT, Notes TEXT, ea_guid TEXT);

    CREATE TABLE t_genopt (AppliesTo TEXT, OptionType TEXT, OptionValue TEXT);
    CREATE TABLE t_objecttypes (Object_Type TEXT, ObjectName TEXT, Notes TEXT, Diagram_Type TEXT);
    CREATE TABLE t_connectortypes (Connector_Type TEXT, Description TEXT, ListItem TEXT, HasState INTEGER);
    CREATE TABLE t_diagramtypes (Diagram_Type TEXT, Name TEXT, Package_ID INTEGER);
    CREATE TABLE t_stereotypes (Stereotype TEXT, AppliesTo TEXT, Description TEXT, Style TEXT,
        metafileLneg TEXT, metafileLpos TEXT, metafileSneg TEXT, metafileSpos TEXT,
        Hidden INTEGER, ProjectStyle TEXT, Notes TEXT, VisualType TEXT, StereotypeGUID TEXT);
    CREATE TABLE t_secpolicies (PolicyID INTEGER PRIMARY KEY, Name TEXT, Active INTEGER);
    CREATE TABLE usys_system (LastObjectID INTEGER, LastDiagramID INTEGER,
        LastConnectorID INTEGER, LastTaskID INTEGER, LastViewID INTEGER, RowVersion TEXT);
    """)

    # --- seed minimal reference data (so EA recognises the project) -------
    cur.execute("INSERT INTO t_genopt VALUES (?,?,?)", ("Repository", "Version", "16.0"))
    cur.execute("INSERT INTO t_genopt VALUES (?,?,?)", ("Model", "Type", "EA"))
    diagram_types = [("Logical", "Class", 0), ("Deployment", "Deployment", 0),
                     ("Component", "Component", 0), ("Use Case", "Use Case", 0)]
    cur.executemany("INSERT INTO t_diagramtypes VALUES (?,?,?)", diagram_types)
    obj_types = [("Class", "Class", "", "Logical"), ("Component", "Component", "", "Component"),
                 ("Node", "Node", "", "Deployment"), ("Artifact", "Artifact", "", "Deployment"),
                 ("Enumeration", "Enumeration", "", "Logical"), ("Package", "Package", "", "")]
    cur.executemany("INSERT INTO t_objecttypes VALUES (?,?,?,?)", obj_types)
    conn_types = [("Dependency", "Dependency", "", 0), ("Generalization", "Generalization", "", 0),
                  ("Association", "Association", "", 0), ("Usage", "Usage", "", 0),
                  ("Deployment", "Deployment", "", 0), ("Manifest", "Manifest", "", 0)]
    cur.executemany("INSERT INTO t_connectortypes VALUES (?,?,?,?)", conn_types)

    # --- packages (+ matching package objects in t_object) ---------------
    # EA element ids and package ids share the t_object space via PDATA1.
    # We offset object ids for packages to keep them unique.
    pkg_obj_offset = 100000
    for p in model.packages:
        cur.execute(
            "INSERT INTO t_package (Package_ID,Name,Parent_ID,CreatedDate,ModifiedDate,"
            "Notes,ea_guid,IsControlled,Protected,IsNamespace,TPos,BatchSave,BatchLoad,"
            "UseDTD,LogXML,UMLVersion,UseModelGen) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (p["id"], p["name"], p["parent_id"], NOW, NOW, p["notes"], p["guid"],
             0, 0, 1, p["id"], 0, 0, 0, 0, "2.5", 0))
        if p["parent_id"] != 0:
            oid = pkg_obj_offset + p["id"]
            cur.execute(
                "INSERT INTO t_object (Object_ID,Object_Type,Name,Note,Package_ID,"
                "CreatedDate,ModifiedDate,ea_guid,PDATA1,ParentID,Scope) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (oid, "Package", p["name"], p["notes"], p["parent_id"], NOW, NOW,
                 guid(), str(p["id"]), 0, "Public"))

    # --- elements --------------------------------------------------------
    for e in model.elements:
        cur.execute(
            "INSERT INTO t_object (Object_ID,Object_Type,Name,Note,Package_ID,Stereotype,"
            "CreatedDate,ModifiedDate,ea_guid,Abstract,Scope,ParentID,Status,Visibility) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (e["id"], e["type"], e["name"], e["notes"], e["package_id"], e["stereotype"],
             NOW, NOW, e["guid"], "1" if e["abstract"] else "0", "Public", 0, "Proposed", "Public"))
        pos = 0
        for a in e["attrs"]:
            pos += 1
            aname, atype = (a + ("",))[:2] if isinstance(a, tuple) else (a, "")
            cur.execute(
                "INSERT INTO t_attribute (Object_ID,Name,Scope,Type,Pos,ea_guid,"
                "LowerBound,UpperBound,Object_Type) VALUES (?,?,?,?,?,?,?,?,?)",
                (e["id"], aname, "Private", atype, pos, guid(), "1", "1", "Attribute"))
        pos = 0
        for o in e["ops"]:
            pos += 1
            oname, otype, onote = (list(o) + ["", ""])[:3]
            cur.execute(
                "INSERT INTO t_operation (Object_ID,Name,Scope,Type,Pos,ea_guid,Notes) "
                "VALUES (?,?,?,?,?,?,?)",
                (e["id"], oname, "Public", otype, pos, guid(), onote))

    # --- connectors ------------------------------------------------------
    for c in model.connectors:
        cur.execute(
            "INSERT INTO t_connector (Connector_ID,Name,Connector_Type,Notes,"
            "Start_Object_ID,End_Object_ID,SourceCard,DestCard,Stereotype,ea_guid,"
            "SeqNo,DestRole,SourceRole) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (c["id"], c["name"], c["type"], c["notes"], c["src"], c["dst"],
             c["src_card"], c["dst_card"], c["stereotype"], c["guid"], 0, "", ""))

    # --- diagrams + placement -------------------------------------------
    inst = 0
    link_inst = 0
    for d in model.diagrams:
        cur.execute(
            "INSERT INTO t_diagram (Diagram_ID,Package_ID,Diagram_Type,Name,Notes,"
            "CreatedDate,ModifiedDate,ea_guid,Scale,ShowDetails,Orientation,cx,cy) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (d["id"], d["package_id"], d["type"], d["name"], d["notes"], NOW, NOW,
             d["guid"], 100, 0, "P", 827, 1169))
        # auto grid layout
        cols = 4
        cell_w, cell_h = 220, 150
        box_w, box_h = 170, 90
        placed = {}
        for idx, eid in enumerate(d["elems"]):
            inst += 1
            col = idx % cols
            row = idx // cols
            left = 30 + col * cell_w
            top = 30 + row * cell_h
            right = left + box_w
            bottom = top + box_h
            # EA stores Y downward as negative
            cur.execute(
                "INSERT INTO t_diagramobjects (Diagram_ID,Object_ID,RectTop,RectLeft,"
                "RectRight,RectBottom,Sequence,Instance_ID) VALUES (?,?,?,?,?,?,?,?)",
                (d["id"], eid, -top, left, right, -bottom, idx + 1, inst))
            placed[eid] = True
        # add connector links whose both ends are on the diagram
        for c in model.connectors:
            if c["src"] in placed and c["dst"] in placed:
                link_inst += 1
                cur.execute(
                    "INSERT INTO t_diagramlinks (DiagramID,ConnectorID,Geometry,Style,"
                    "Hidden,Instance_ID) VALUES (?,?,?,?,?,?)",
                    (d["id"], c["id"], "", "", 0, link_inst))

    # --- usys_system bookkeeping ----------------------------------------
    last_obj = pkg_obj_offset + len(model.packages) + 10
    cur.execute("INSERT INTO usys_system (LastObjectID,LastDiagramID,LastConnectorID,"
                "LastTaskID,LastViewID,RowVersion) VALUES (?,?,?,?,?,?)",
                (last_obj, len(model.diagrams) + 1, len(model.connectors) + 1, 1, 1, "1"))

    db.commit()
    db.close()


# ===========================================================================
#  XMI 2.1 emitter (UML 2 + EA extensions) - reliable import fallback
# ===========================================================================
def xml_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def xmi_id(prefix, n):
    return "EAID_%s%08d" % (prefix, n)


UML_TYPE = {
    "Class": "uml:Class", "Component": "uml:Component", "Node": "uml:Node",
    "Artifact": "uml:Artifact", "Enumeration": "uml:Enumeration",
}
CONN_UML = {
    "Generalization": "uml:Generalization", "Association": "uml:Association",
    "Dependency": "uml:Dependency", "Usage": "uml:Usage",
    "Deploy": "uml:Dependency", "Manifest": "uml:Abstraction",
}


def emit_xmi(model, path):
    by_pkg_children = {}
    for p in model.packages:
        by_pkg_children.setdefault(p["parent_id"], []).append(p)
    elems_by_pkg = {}
    for e in model.elements:
        elems_by_pkg.setdefault(e["package_id"], []).append(e)

    def eid(e): return xmi_id("E", e["id"])
    def pid(p): return "EAPK_%08d" % p["id"]

    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<xmi:XMI xmi:version="2.1" xmlns:uml="http://schema.omg.org/spec/UML/2.1" '
               'xmlns:xmi="http://schema.omg.org/spec/XMI/2.1">')
    out.append('  <xmi:Documentation exporter="znalosti.gov.sk model generator" '
               'exporterVersion="1.0"/>')
    out.append('  <uml:Model xmi:type="uml:Model" name="EA_Model" xmi:id="EAID_MODEL">')

    def render_package(p, indent):
        pad = "  " * indent
        out.append('%s<packagedElement xmi:type="uml:Package" xmi:id="%s" name="%s">'
                   % (pad, pid(p), xml_escape(p["name"])))
        # nested packages
        for child in by_pkg_children.get(p["id"], []):
            render_package(child, indent + 1)
        # elements
        for e in elems_by_pkg.get(p["id"], []):
            render_element(e, indent + 1)
        # connectors owned where source resides
        for c in model.connectors:
            src = elem_index.get(c["src"])
            if src and src["package_id"] == p["id"]:
                render_connector(c, indent + 1)
        out.append('%s</packagedElement>' % pad)

    def render_element(e, indent):
        pad = "  " * indent
        utype = UML_TYPE.get(e["type"], "uml:Class")
        attrs = ' isAbstract="true"' if e["abstract"] else ""
        out.append('%s<packagedElement xmi:type="%s" xmi:id="%s" name="%s"%s>'
                   % (pad, utype, eid(e), xml_escape(e["name"]), attrs))
        if e["type"] == "Enumeration":
            for a in e["attrs"]:
                aname = a[0] if isinstance(a, tuple) else a
                out.append('%s  <ownedLiteral xmi:type="uml:EnumerationLiteral" '
                           'xmi:id="%s_L%s" name="%s"/>'
                           % (pad, eid(e), xml_escape(aname), xml_escape(aname)))
        else:
            for i, a in enumerate(e["attrs"]):
                aname, atype = (a + ("",))[:2] if isinstance(a, tuple) else (a, "")
                out.append('%s  <ownedAttribute xmi:type="uml:Property" xmi:id="%s_A%d" '
                           'name="%s" visibility="private"/>'
                           % (pad, eid(e), i, xml_escape(aname)))
            for i, o in enumerate(e["ops"]):
                oname = o[0]
                out.append('%s  <ownedOperation xmi:type="uml:Operation" xmi:id="%s_O%d" '
                           'name="%s" visibility="public"/>'
                           % (pad, eid(e), i, xml_escape(oname)))
        # generalizations belonging to this element
        for c in model.connectors:
            if c["type"] == "Generalization" and c["src"] == e["id"]:
                out.append('%s  <generalization xmi:type="uml:Generalization" '
                           'xmi:id="%s" general="%s"/>'
                           % (pad, xmi_id("G", c["id"]), eid(elem_index[c["dst"]])))
        out.append('%s</packagedElement>' % pad)

    def render_connector(c, indent):
        if c["type"] == "Generalization":
            return  # rendered inside the element
        pad = "  " * indent
        utype = CONN_UML.get(c["type"], "uml:Dependency")
        src = eid(elem_index[c["src"]])
        dst = eid(elem_index[c["dst"]])
        cid = xmi_id("C", c["id"])
        nm = (' name="%s"' % xml_escape(c["name"])) if c["name"] else ""
        if utype == "uml:Association":
            out.append('%s<packagedElement xmi:type="uml:Association" xmi:id="%s"%s>'
                       % (pad, cid, nm))
            out.append('%s  <memberEnd xmi:idref="%s_end1"/>' % (pad, cid))
            out.append('%s  <memberEnd xmi:idref="%s_end2"/>' % (pad, cid))
            out.append('%s  <ownedEnd xmi:type="uml:Property" xmi:id="%s_end1" type="%s"/>'
                       % (pad, cid, src))
            out.append('%s  <ownedEnd xmi:type="uml:Property" xmi:id="%s_end2" type="%s"/>'
                       % (pad, cid, dst))
            out.append('%s</packagedElement>' % pad)
        else:
            out.append('%s<packagedElement xmi:type="%s" xmi:id="%s"%s client="%s" supplier="%s"/>'
                       % (pad, utype, cid, nm, src, dst))

    elem_index = {e["id"]: e for e in model.elements}

    # root model package is the EA "Model" container
    root_pkg = [p for p in model.packages if p["parent_id"] == 0][0]
    render_package(root_pkg, 2)

    out.append('  </uml:Model>')

    # --- EA-native extension (elements + connectors + diagrams) ----------
    # Enterprise Architect reconstructs diagrams from this extension. It needs
    # the <elements> and <connectors> lists so that diagram element "subject"
    # references resolve; without them EA imports the model tree but drops the
    # diagrams (the problem we are fixing here).
    pkg_index = {p["id"]: p for p in model.packages}
    EA_STYPE = {"Class": "Class", "Component": "Component", "Node": "Node",
                "Artifact": "Artifact", "Enumeration": "Enumeration"}
    EA_CONN_TYPE = {"Deploy": "Deployment"}
    AUTHOR = "znalosti.gov.sk model generator"

    out.append('  <xmi:Extension extender="Enterprise Architect" extenderID="6.5">')

    # ---- elements (packages + classifiers) ----
    out.append('    <elements>')
    for p in model.packages:
        if p["parent_id"] == 0:
            continue  # root maps onto the EA model node
        parent_ref = ("EAPK_%08d" % p["parent_id"]) if p["parent_id"] != 0 else "EAID_MODEL"
        out.append('      <element xmi:idref="%s" xmi:type="uml:Package" name="%s" scope="public">'
                   % (pid(p), xml_escape(p["name"])))
        out.append('        <model package="%s" ea_localid="%d" ea_eleType="package"/>'
                   % (parent_ref, 100000 + p["id"]))
        out.append('        <properties isSpecification="false" sType="Package" nType="0" scope="public"/>')
        out.append('        <project author="%s" version="1.0" phase="1.0" created="%s" '
                   'modified="%s" complexity="2" status="Proposed"/>' % (AUTHOR, NOW, NOW))
        out.append('        <style appearance="BackColor=-1;BorderColor=-1;BorderWidth=-1;'
                   'FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;"/>')
        if p["notes"]:
            out.append('        <documentation value="%s"/>' % xml_escape(p["notes"]))
        out.append('      </element>')
    for e in model.elements:
        stype = EA_STYPE.get(e["type"], "Class")
        absx = ' isAbstract="true"' if e["abstract"] else ''
        out.append('      <element xmi:idref="%s" xmi:type="%s" name="%s" scope="public">'
                   % (eid(e), UML_TYPE.get(e["type"], "uml:Class"), xml_escape(e["name"])))
        out.append('        <model package="EAPK_%08d" ea_localid="%d" ea_eleType="element"/>'
                   % (e["package_id"], e["id"]))
        out.append('        <properties isSpecification="false" sType="%s" nType="0" '
                   'scope="public"%s/>' % (stype, absx))
        out.append('        <project author="%s" version="1.0" phase="1.0" created="%s" '
                   'modified="%s" complexity="2" status="Proposed"/>' % (AUTHOR, NOW, NOW))
        if e["stereotype"]:
            out.append('        <stereotype stereotype="%s"/>' % xml_escape(e["stereotype"]))
        out.append('        <style appearance="BackColor=-1;BorderColor=-1;BorderWidth=-1;'
                   'FontColor=-1;VSwimLanes=1;HSwimLanes=1;BorderStyle=0;"/>')
        if e["notes"]:
            out.append('        <documentation value="%s"/>' % xml_escape(e["notes"]))
        out.append('      </element>')
    out.append('    </elements>')

    # ---- connectors ----
    out.append('    <connectors>')
    for c in model.connectors:
        src = elem_index[c["src"]]
        dst = elem_index[c["dst"]]
        ea_type = EA_CONN_TYPE.get(c["type"], c["type"])
        nm = (' name="%s"' % xml_escape(c["name"])) if c["name"] else ''
        out.append('      <connector xmi:idref="%s"%s>' % (xmi_id("C", c["id"]), nm))
        out.append('        <source xmi:idref="%s">' % eid(src))
        out.append('          <model ea_localid="%d" type="%s" name="%s"/>'
                   % (src["id"], EA_STYPE.get(src["type"], "Class"), xml_escape(src["name"])))
        out.append('          <role visibility="Public"/>')
        out.append('          <type aggregation="none" containment="Unspecified"/>')
        out.append('        </source>')
        out.append('        <target xmi:idref="%s">' % eid(dst))
        out.append('          <model ea_localid="%d" type="%s" name="%s"/>'
                   % (dst["id"], EA_STYPE.get(dst["type"], "Class"), xml_escape(dst["name"])))
        out.append('          <role visibility="Public"/>')
        out.append('          <type aggregation="none" containment="Unspecified"/>')
        out.append('        </target>')
        out.append('        <properties ea_type="%s" direction="Source -&gt; Destination"/>'
                   % xml_escape(ea_type))
        out.append('        <appearance linemode="3" linecolor="-1" linewidth="0" seqno="0" '
                   'headStyle="0" lineStyle="0"/>')
        out.append('      </connector>')
    out.append('    </connectors>')

    # ---- diagrams ----
    out.append('    <diagrams>')
    cols, cell_w, cell_h, box_w, box_h = 4, 220, 150, 170, 90
    for d in model.diagrams:
        pkg_ref = "EAPK_%08d" % d["package_id"]
        out.append('      <diagram xmi:id="EAID_DGM%08d">' % d["id"])
        out.append('        <model package="%s" localID="%d" owner="%s"/>'
                   % (pkg_ref, d["id"], pkg_ref))
        out.append('        <properties name="%s" type="%s"/>'
                   % (xml_escape(d["name"]), xml_escape(d["type"])))
        out.append('        <project author="%s" version="1.0" created="%s" modified="%s"/>'
                   % (AUTHOR, NOW, NOW))
        out.append('        <style1 value="ShowPrivate=1;ShowProtected=1;ShowPublic=1;'
                   'HideRelationships=0;Locked=0;Border=1;HighlightForeign=1;PackageContents=1;'
                   'SequenceNotes=0;ScalePrintImage=0;PPgs.cx=0;PPgs.cy=0;DocSize.cx=826;'
                   'DocSize.cy=1169;ShowDetails=0;Orientation=P;Zoom=100;"/>')
        # nodes
        out.append('        <elements>')
        placed = set()
        for idx, e_id in enumerate(d["elems"]):
            col, rrow = idx % cols, idx // cols
            left = 30 + col * cell_w
            top = 30 + rrow * cell_h
            geom = "Left=%d;Top=%d;Right=%d;Bottom=%d;" % (left, top, left + box_w, top + box_h)
            out.append('          <element geometry="%s" subject="%s" seqno="%d" style="DUID=%08d;"/>'
                       % (geom, eid(elem_index[e_id]), idx + 1, e_id))
            placed.add(e_id)
        out.append('        </elements>')
        out.append('      </diagram>')
    out.append('    </diagrams>')

    out.append('  </xmi:Extension>')
    out.append('</xmi:XMI>')

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # NOTE: We intentionally emit ONLY the XMI artifact.
    #
    # A standalone, hand-written .qea cannot be opened by Enterprise Architect:
    # EA validates a complete, version-stamped base schema (~200 system tables +
    # seed rows that ship only inside EA's own EABase.qea template) and rejects
    # anything else with "Sparx Systems Database API [0x00001086]".
    #
    # The supported way to obtain a real .qea is to let EA create the file
    # (File > New Project, which clones EABase.qea) and then import this XMI
    # (Publish > Model Exchange > Import Package from XMI). See README.md.
    #
    # The emit_qea() function is kept for reference only and is not called.
    emit_xmi(m, XMI_PATH)
    print("Packages : %d" % len(m.packages))
    print("Elements : %d" % len(m.elements))
    print("Connectors: %d" % len(m.connectors))
    print("Diagrams : %d" % len(m.diagrams))
    print("Wrote: %s (%d bytes)" % (XMI_PATH, os.path.getsize(XMI_PATH)))
