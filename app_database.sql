
START TRANSACTION;
CREATE TABLE submissions (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                kg_endpoint TEXT NOT NULL,
                nl_question TEXT NOT NULL,
                sparql_query TEXT,
                username TEXT
            );
INSERT INTO submissions VALUES(1,'https://data.gesis.org/gesiskg/sparql','What are all the concepts in the graph?',NULL,'harshcs.1996@gmail.com');
INSERT INTO submissions VALUES(2,'https://bso.swissartresearch.net/sparql','What are all the named graphs in the KG?',replace(replace('SELECT ?graph\r\nWHERE { \r\n  GRAPH ?graph {}\r\n}','\r',char(13)),'\n',char(10)),'harshcs.1996@gmail.com');
INSERT INTO submissions VALUES(3,'https://lod.ehri-project-test.eu/query/','What are all the countries involved in the study?',NULL,'harshcs.1996@gmail.com');
INSERT INTO submissions VALUES(4,'https://data.gesis.org/gesiskg/sparql',replace(replace('SELECT ?article ?title\r\nWHERE {\r\n  ?article <https://schema.org/about> ?topic.\r\n  ?topic <https://schema.org/name> "Gesundheit"@de.\r\n  ?article ?p <https://schema.org/ScholarlyArticle>.\r\n  ?article <https://schema.org/name> ?title.\r\n}\r\nLIMIT 100','\r',char(13)),'\n',char(10)),replace(replace('SELECT ?article ?title\r\nWHERE {\r\n  ?article <https://schema.org/about> ?topic.\r\n  ?topic <https://schema.org/name> "Gesundheit"@de.\r\n  ?article ?p <https://schema.org/ScholarlyArticle>.\r\n  ?article <https://schema.org/name> ?title.\r\n}\r\nLIMIT 100\r\n','\r',char(13)),'\n',char(10)),'yurui.zhu@outlook.com');
INSERT INTO submissions VALUES(5,'https://data.gesis.org/gesiskg/sparql',replace(replace('SELECT ?publication ?dataset ?score\r\nWHERE {\r\n  ?link a <https://w3id.org/gesiskg/LinkMetadata> ;\r\n        <https://w3id.org/gesiskg/linkingMethod> "automatic" ;\r\n        <https://w3id.org/gesiskg/linkScore> ?score ;\r\n        <https://w3id.org/gesiskg/reference> ?pubRef , ?datasetRef .\r\n\r\n  FILTER (?score > 0.9)\r\n\r\n  ?pubRef a <https://w3id.org/gesiskg/PublicationReference> ;\r\n          <https://schema.org/mainEntity> ?publication .\r\n  ?datasetRef a <https://w3id.org/gesiskg/DatasetReference> ;\r\n              <https://schema.org/mainEntity> ?dataset .\r\n}\r\nLIMIT 100','\r',char(13)),'\n',char(10)),replace(replace('SELECT ?publication ?dataset ?score\r\nWHERE {\r\n  ?link a <https://w3id.org/gesiskg/LinkMetadata> ;\r\n        <https://w3id.org/gesiskg/linkingMethod> "automatic" ;\r\n        <https://w3id.org/gesiskg/linkScore> ?score ;\r\n        <https://w3id.org/gesiskg/reference> ?pubRef , ?datasetRef .\r\n\r\n  FILTER (?score > 0.9)\r\n\r\n  ?pubRef a <https://w3id.org/gesiskg/PublicationReference> ;\r\n          <https://schema.org/mainEntity> ?publication .\r\n  ?datasetRef a <https://w3id.org/gesiskg/DatasetReference> ;\r\n              <https://schema.org/mainEntity> ?dataset .\r\n}\r\nLIMIT 100','\r',char(13)),'\n',char(10)),'yurui.zhu@outlook.com');
INSERT INTO submissions VALUES(6,'https://bio2rdf.org/sparql','What is the licensing information for all datasets?',replace(replace('PREFIX void: <http://rdfs.org/ns/void#>\r\nPREFIX dcterms: <http://purl.org/dc/terms/>\r\n\r\nSELECT ?dataset ?license\r\nWHERE {\r\n  ?dataset a void:Dataset ;\r\n           dcterms:rights ?license .\r\n}','\r',char(13)),'\n',char(10)),'yurui.zhu@outlook.com');
INSERT INTO submissions VALUES(7,'https://bio2rdf.org/sparql','Get all triples involving the PharmGKB Resource for Ehlers-Danlos Syndrome ','DESCRIBE <http://bio2rdf.org/pharmgkb:PA443997>','yurui.zhu@outlook.com');
INSERT INTO submissions VALUES(8,'https://lod.ehri-project-test.eu/query/',replace(replace('What is the average number of archival documents per institution by country of provenance?\r\n\r\n[Source: https://lod.ehri-project-test.eu/]','\r',char(13)),'\n',char(10)),replace(replace('PREFIX db: <http://dbpedia.org/>\r\nPREFIX dbp: <http://dbpedia.org/property/>\r\nPREFIX rico: <https://www.ica.org/standards/RiC/ontology#>\r\nPREFIX dbo: <http://dbpedia.org/ontology/>\r\nPREFIX owl: <http://www.w3.org/2002/07/owl#>\r\nPREFIX schema: <http://schema.org/>\r\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\r\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\r\nPREFIX ehri:  <http://lod.ehri-project-test.eu/>\r\nPREFIX ehri_institutions: <http://lod.ehri-project-test.eu/institutions/>\r\nPREFIX ehri_units: <http://lod.ehri-project-test.eu/units/>\r\nPREFIX ehri_countries: <http://lod.ehri-project-test.eu/countries/>\r\nSELECT ?country (AVG(?totalRecordByInstitution) as ?meanByCountry) WHERE {\r\n	?country a rico:Place ;\r\n			rico:containsOrContained ?institution .\r\n		{\r\n			SELECT ?institution (COUNT(?record) as ?totalRecordByInstitution) WHERE {\r\n				?institution a rico:CorporateBody ;\r\n					rico:isOrWasHolderOf ?instantiation .\r\n				?instantiation a rico:Instantiation ;\r\n					rico:isInstantiationOf ?record .\r\n				?record a rico:Record .\r\n			} GROUP BY ?institution\r\n		}\r\n		\r\n} GROUP BY ?country','\r',char(13)),'\n',char(10)),'matteo.romanello@gmail.com');
INSERT INTO submissions VALUES(9,'https://data.gesis.org/gesiskg/sparql','Give me 100 new triplets at random',NULL,'0009-0001-8468-3237');
INSERT INTO submissions VALUES(10,'https://data.gesis.org/gesiskg/sparql','What are all the concepts present in the Scholarly Article?',NULL,'harshdeep.singh@odoma.ch');
INSERT INTO submissions VALUES(11,'https://bso.swissartresearch.net/sparql','Give me 10 random triplets',replace(replace('SELECT DISTINCT ?node WHERE {\r\n  ?node ?p ?o .\r\n  BIND(RAND() AS ?random)\r\n} \r\nORDER BY ?random\r\nLIMIT 10','\r',char(13)),'\n',char(10)),'harshcs.1996@gmail.com');
INSERT INTO submissions VALUES(12,'https://triplydb.com/smithsonian/american-art-museum/sparql','What are all the concepts present?',NULL,'harshcs.1996@gmail.com');
CREATE TABLE kg_endpoints (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
INSERT INTO kg_endpoints VALUES(1,'Gesis','Social science research data','https://data.gesis.org/gesiskg/sparql','2025-06-20 08:12:06');
INSERT INTO kg_endpoints VALUES(2,'Swiss Art Research - BSO','Swiss art and cultural heritage knowledge graph','https://bso.swissartresearch.net/sparql','2025-06-20 08:12:06');
INSERT INTO kg_endpoints VALUES(3,'Smithsonian Art Museum KG','Smithsonian Institution art and cultural collections','https://triplydb.com/smithsonian/american-art-museum/sparql','2025-06-20 08:12:06');
INSERT INTO kg_endpoints VALUES(4,'EHRI','European Holocaust Research Infrastructure','https://lod.ehri-project-test.eu/query/','2025-06-20 08:13:52');
INSERT INTO kg_endpoints VALUES(5,'Bio2RDF ','Semantic Web technologies to build and provide the largest network of Linked Data for the Life Sciences. ','https://bio2rdf.org/sparql','2025-06-20 08:47:21');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('kg_endpoints',5);
INSERT INTO sqlite_sequence VALUES('submissions',12);
COMMIT;
