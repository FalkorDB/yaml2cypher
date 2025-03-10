# yaml2cypher

A Python tool to convert YAML files to Cypher queries for graph databases like FalkorDB and Neo4j.

## Features

- Convert structured YAML files to Cypher CREATE statements
- Support for nodes with labels and properties
- Support for relationships with types and properties
- Command-line interface for easy integration
- Proper property value formatting for Cypher

## Installation

### From PyPI (recommended)

```bash
pip install yaml2cypher
```

### Using Poetry (for development)

```bash
git clone https://github.com/yourusername/yaml2cypher.git
cd yaml2cypher
poetry install
```

To run the tool using Poetry:

```bash
poetry run yaml2cypher example.yaml
```

Or activate the virtual environment:

```bash
poetry shell
yaml2cypher example.yaml
```

## Usage

### Command Line

Convert a YAML file to Cypher:

```bash
yaml2cypher example.yaml
```

This will create `example.cypher` with the generated Cypher queries.

Specify an output file:

```bash
yaml2cypher example.yaml -o output.cypher
```

Enable verbose logging:

```bash
yaml2cypher example.yaml -v
```

### Python API

```python
from yaml2cypher import YAML2Cypher

# Initialize the converter
converter = YAML2Cypher()

# Convert a YAML file to Cypher statements
cypher_statements = converter.yaml_file_to_cypher('example.yaml')

# Write statements to a file
converter.write_cypher_to_file(cypher_statements, 'output.cypher')

# Or use the statements directly
for statement in cypher_statements:
    print(statement)
```

## YAML Format

The tool expects YAML files with the following structure:

```yaml
nodes:
  node_id:
    labels: LabelName  # Or a list of labels
    property1: value1
    property2: value2

relationships:
  - from: source_node_id
    to: target_node_id
    type: RELATIONSHIP_TYPE
    property1: value1
    property2: value2
```

### Example

```yaml
nodes:
  person1:
    labels: Person
    name: "John Doe"
    age: 30
  
  company1:
    labels: 
      - Company
      - Organization
    name: "Graph Solutions Inc."

relationships:
  - from: person1
    to: company1
    type: WORKS_FOR
    position: "Software Engineer"
```

This will generate the following Cypher:

```cypher
CREATE (person1:Person {name: 'John Doe', age: 30});
CREATE (company1:Company:Organization {name: 'Graph Solutions Inc.'});
CREATE (person1)-[:WORKS_FOR {position: 'Software Engineer'}]->(company1);
```

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.