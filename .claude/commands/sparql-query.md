Execute a SPARQL query against the knowledge graph.

Usage: Provide the SPARQL query as argument, e.g. `/sparql-query SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10`

The query will be sent to the local API endpoint at http://localhost:8080/api/sparql via curl.

```bash
curl -X POST "http://localhost:8080/api/sparql" \
  -H "Accept: application/sparql-results+json" \
  --data-urlencode "q=$ARGUMENTS"
```

Format the results in a readable table.
