// Load Nodes from CSV
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CALL {
  WITH row
  CALL apoc.create.node([row.type], 
    {id: row.id, label: row.label, 
     tags: apoc.convert.fromJsonList(row.tags),
     properties: apoc.convert.fromJsonMap(row.properties)}
  ) YIELD node
  RETURN node
} IN TRANSACTIONS OF 500 ROWS;

// Load Edges from CSV
LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
CALL {
  WITH row
  MATCH (a {id: row.source})
  MATCH (b {id: row.target})
  CALL apoc.create.relationship(a, row.type, {}, b) YIELD rel
  RETURN rel
} IN TRANSACTIONS OF 1000 ROWS;
