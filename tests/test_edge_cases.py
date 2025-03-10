import pytest
import tempfile
import yaml
import os
from yaml2cypher import YAML2Cypher


@pytest.fixture
def converter():
    """Create a YAML2Cypher instance for testing."""
    return YAML2Cypher()


def test_empty_yaml():
    """Test handling of empty YAML files."""
    converter = YAML2Cypher()
    
    # Empty dict
    statements = converter.convert_yaml_to_cypher({})
    assert statements == []
    
    # Empty nodes and relationships
    statements = converter.convert_yaml_to_cypher({"nodes": {}, "relationships": []})
    assert statements == []


def test_special_characters():
    """Test handling of special characters in property values."""
    converter = YAML2Cypher()
    
    # Test with quote characters
    assert converter._format_property_value("O'Reilly") == "'O\\'Reilly'"
    assert converter._format_property_value("\"Quoted\"") == "'\"Quoted\"'"
    
    # Test with newlines and other special chars
    assert converter._format_property_value("Line 1\nLine 2") == "'Line 1\nLine 2'"
    assert converter._format_property_value("Tab\tCharacter") == "'Tab\tCharacter'"


def test_nested_structures():
    """Test handling of nested structures in property values."""
    converter = YAML2Cypher()
    
    # Test with nested dictionaries
    nested_dict = {"person": {"name": "John", "age": 30}}
    expected = "{person: {name: 'John', age: 30}}"
    assert converter._format_property_value(nested_dict) == expected
    
    # Test with nested lists
    nested_list = [1, [2, 3], 4]
    expected = "[1, [2, 3], 4]"
    assert converter._format_property_value(nested_list) == expected
    
    # Test with complex nested structure
    complex_structure = {
        "data": [
            {"id": 1, "values": [10, 20]},
            {"id": 2, "values": [30, 40]}
        ]
    }
    formatted = converter._format_property_value(complex_structure)
    assert "data: [" in formatted
    assert "{id: 1, values: [10, 20]}" in formatted
    assert "{id: 2, values: [30, 40]}" in formatted


def test_invalid_yaml_file():
    """Test handling of invalid YAML files."""
    converter = YAML2Cypher()
    
    # Create a file with invalid YAML
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w') as f:
        f.write("this is not valid yaml: : :")
        invalid_file = f.name
    
    try:
        # Should raise an exception
        with pytest.raises(Exception):
            converter.load_yaml(invalid_file)
    
    finally:
        # Clean up
        if os.path.exists(invalid_file):
            os.unlink(invalid_file)


def test_missing_labels_field():
    """Test handling of nodes without a labels field."""
    converter = YAML2Cypher()
    
    data = {
        "nodes": {
            "person1": {
                "name": "John",
                "age": 30
            }
        }
    }
    
    statements = converter.convert_yaml_to_cypher(data)
    assert len(statements) == 1
    assert statements[0] == "CREATE (person1 {name: 'John', age: 30})"


def test_unconventional_yaml_structure():
    """Test handling of YAML structures that don't match expected schema."""
    converter = YAML2Cypher()
    
    # Structure with no 'nodes' or 'relationships' keys
    data = {
        "something_else": {
            "key1": "value1"
        }
    }
    
    statements = converter.convert_yaml_to_cypher(data)
    assert statements == []


def test_relationship_without_required_fields():
    """Test handling of relationships missing required fields."""
    converter = YAML2Cypher()
    
    data = {
        "relationships": [
            {"from": "node1", "to": "node2"},  # Missing 'type'
            {"from": "node1", "type": "RELATES_TO"},  # Missing 'to'
            {"to": "node2", "type": "RELATES_TO"}  # Missing 'from'
        ]
    }
    
    statements = converter.convert_yaml_to_cypher(data)
    assert statements == []


def test_utf8_characters():
    """Test handling of UTF-8 characters in property values."""
    converter = YAML2Cypher()
    
    # Test with non-ASCII characters
    assert converter._format_property_value("こんにちは") == "'こんにちは'"
    assert converter._format_property_value("ñ") == "'ñ'"
    assert converter._format_property_value("€") == "'€'"
    
    # Create YAML with UTF-8 characters
    data = {
        "nodes": {
            "person1": {
                "labels": "Person",
                "name": "José Martínez",
                "location": "München"
            }
        }
    }
    
    statements = converter.convert_yaml_to_cypher(data)
    assert statements[0] == "CREATE (person1:Person {name: 'José Martínez', location: 'München'})"