CREATE (person1:Person {name: 'John Doe', age: 30, active: true, skills: ['Python', 'Graph Databases']});
CREATE (person2:Person {name: 'Jane Smith', age: 28, active: true, skills: ['Cypher', 'YAML']});
CREATE (company1:Company:Organization {name: 'Graph Solutions Inc.', founded: 2010, location: 'San Francisco'});
CREATE (person1)-[:KNOWS {since: 2018, strength: 0.8}]->(person2);
CREATE (person1)-[:WORKS_FOR {position: 'Software Engineer', since: 2019}]->(company1);
CREATE (person2)-[:WORKS_FOR {position: 'Data Scientist', since: 2020}]->(company1);
