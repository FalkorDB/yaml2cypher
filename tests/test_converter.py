import pytest
import os
import tempfile
import yaml
from yaml2cypher import YAML2Cypher


@pytest.fixture
def converter():
    """Create a YAML2Cypher instance for testing."""
    return YAML2Cypher()


@pytest.fixture
def sample_yaml_data():
    """Sample YAML data for testing."""
    return {
        "nodes": {
            "person1": {
                "labels": "Person",
                "name": "John Doe",
                "age": 30,
                "active": True
            },
            "company1": {
                "labels": ["Company", "Organization"],
                "name": "ACME Inc.",
                "founded": 1999
            }
        },
        "relationships": [
            {
                "from": "person1",
                "to": "company1",
                "type": "WORKS_FOR",
                "since": 2015,
                "position": "Developer"
            }
        ]
    }


@pytest.fixture
def sample_yaml_file(sample_yaml_data):
    """Create a temporary YAML file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w') as f:
        yaml.dump(sample_yaml_data, f)
        temp_file_path = f.name

    yield temp_file_path

    # Cleanup after test
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_load_yaml(converter, sample_yaml_file, sample_yaml_data):
    """Test loading YAML from a file."""
    loaded_data = converter.load_yaml(sample_yaml_file)
    assert loaded_data == sample_yaml_data


def test_format_property_value(converter):
    """Test property value formatting for Cypher."""
    # Test string formatting
    assert converter._format_property_value("test") == "'test'"
    assert converter._format_property_value("It's a test") == "'It\\'s a test'"

    # Test other types
    assert converter._format_property_value(None) == "null"
    assert converter._format_property_value(True) == "true"
    assert converter._format_property_value(False) == "false"
    assert converter._format_property_value(42) == "42"
    assert converter._format_property_value(3.14) == "3.14"

    # Test lists
    assert converter._format_property_value(["a", "b"]) == "['a', 'b']"
    assert converter._format_property_value([1, 2, 3]) == "[1, 2, 3]"

    # Test dictionaries
    assert converter._format_property_value({"name": "John", "age": 30}) == "{name: 'John', age: 30}"


def test_generate_node_properties(converter):
    """Test generation of node properties for Cypher."""
    properties = {"name": "John", "age": 30, "active": True}
    assert converter._generate_node_properties(properties) == "{name: 'John', age: 30, active: true}"

    # Test empty properties
    assert converter._generate_node_properties({}) == ""


def test_convert_node(converter):
    """Test conversion of a node to Cypher CREATE statement."""
    # Test with single label
    node_data = {"labels": "Person", "name": "John", "age": 30}
    assert converter._convert_node("p1", node_data) == "CREATE (p1:Person {name: 'John', age: 30})"

    # Test with multiple labels
    node_data = {"labels": ["Person", "Employee"], "name": "John", "age": 30}
    assert converter._convert_node("p1", node_data) == "CREATE (p1:Person:Employee {name: 'John', age: 30})"

    # Test with no labels
    node_data = {"name": "John", "age": 30}
    assert converter._convert_node("p1", node_data) == "CREATE (p1 {name: 'John', age: 30})"


def test_convert_relationship(converter):
    """Test conversion of a relationship to Cypher CREATE statement."""
    # Test with properties
    rel_data = {"from": "p1", "to": "c1", "type": "WORKS_FOR", "since": 2020, "position": "Manager"}
    expected = "CREATE (p1)-[:WORKS_FOR {since: 2020, position: 'Manager'}]->(c1)"
    assert converter._convert_relationship(rel_data) == expected

    # Test without properties
    rel_data = {"from": "p1", "to": "c1", "type": "KNOWS"}
    expected = "CREATE (p1)-[:KNOWS ]->(c1)"
    assert converter._convert_relationship(rel_data) == expected

    # Test with missing fieldsc
    rel_data = {"from": "p1", "type": "KNOWS"}
    assert converter._convert_relationship(rel_data) == ""


def test_convert_yaml_to_cypher(converter, sample_yaml_data):
    """Test conversion of YAML data to Cypher statements."""
    statements = converter.convert_yaml_to_cypher(sample_yaml_data)

    assert len(statements) == 3
    assert statements[0] == "CREATE (person1:Person {name: 'John Doe', age: 30, active: true})"
    assert statements[1] == "CREATE (company1:Company:Organization {name: 'ACME Inc.', founded: 1999})"
    assert statements[2] == "CREATE (person1)-[:WORKS_FOR {since: 2015, position: 'Developer'}]->(company1)"


def test_yaml_file_to_cypher(converter, sample_yaml_file):
    """Test conversion of a YAML file to Cypher statements."""
    statements = converter.yaml_file_to_cypher(sample_yaml_file)
    assert len(statements) == 3
    assert any("person1:Person" in stmt for stmt in statements)
    assert any("company1:Company:Organization" in stmt for stmt in statements)
    assert any("WORKS_FOR" in stmt for stmt in statements)


def test_write_cypher_to_file(converter, sample_yaml_data):
    """Test writing Cypher statements to a file."""
    statements = converter.convert_yaml_to_cypher(sample_yaml_data)

    with tempfile.NamedTemporaryFile(suffix='.cypher', delete=False) as temp_file:
        output_path = temp_file.name

    try:
        converter.write_cypher_to_file(statements, output_path)

        # Check that file exists and contains expected content
        assert os.path.exists(output_path)

        with open(output_path, 'r') as f:
            content = f.read()
            assert "CREATE (person1:Person" in content
            assert "CREATE (company1:Company:Organization" in content
            assert "CREATE (person1)-[:WORKS_FOR" in content

            # Check for semicolons
            lines = content.strip().split('\n')
            assert len(lines) == 3
            assert all(line.endswith(';') for line in lines)

    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)
