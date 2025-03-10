import pytest
import os
import tempfile
import filecmp
from pathlib import Path
from yaml2cypher import YAML2Cypher, main


@pytest.fixture
def complex_yaml_path():
    """Path to the complex sample YAML file."""
    current_dir = Path(__file__).parent
    return str(current_dir / ".." / "examples" / "complex_graph.yaml")


def test_full_conversion_pipeline(complex_yaml_path):
    """Test the complete conversion pipeline from YAML to Cypher."""
    # Create a temporary file for output
    with tempfile.NamedTemporaryFile(suffix='.cypher', delete=False) as temp_file:
        output_path = temp_file.name
    
    try:
        # Run the main function with the sample file
        exit_code = main([complex_yaml_path, '-o', output_path])
        
        # Check that the conversion was successful
        assert exit_code == 0
        assert os.path.exists(output_path)
        
        # Check the content of the output file
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Check for node statements
            assert "CREATE (person1:Person" in content
            assert "CREATE (company1:Company:Organization" in content
            assert "CREATE (product1:Product" in content
            
            # Check for relationship statements
            assert "CREATE (person1)-[:KNOWS" in content
            assert "CREATE (person1)-[:WORKS_FOR" in content
            assert "CREATE (company1)-[:PRODUCES" in content
            
            # Check that all nodes and relationships are present
            lines = content.strip().split('\n')
            assert len(lines) == 11  # 4 nodes + 7 relationships
            
            # Check that each line ends with a semicolon
            assert all(line.endswith(';') for line in lines)
    
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_converter_class_with_complex_file(complex_yaml_path):
    """Test the YAML2Cypher class directly with a complex YAML file."""
    converter = YAML2Cypher()
    statements = converter.yaml_file_to_cypher(complex_yaml_path)
    
    # Verify number of statements
    assert len(statements) == 11  # 4 nodes + 7 relationships
    
    # Check that each type of node is present
    person_nodes = [s for s in statements if ":Person" in s]
    company_nodes = [s for s in statements if ":Company" in s]
    product_nodes = [s for s in statements if ":Product" in s]
    project_nodes = [s for s in statements if ":Project" in s]
    
    assert len(person_nodes) == 2
    assert len(company_nodes) == 1
    assert len(product_nodes) == 1
    assert len(project_nodes) == 1
    
    # Check that each type of relationship is present
    knows_rels = [s for s in statements if "[:KNOWS" in s]
    works_for_rels = [s for s in statements if "[:WORKS_FOR" in s]
    produces_rels = [s for s in statements if "[:PRODUCES" in s]
    works_on_rels = [s for s in statements if "[:WORKS_ON" in s]
    part_of_rels = [s for s in statements if "[:PART_OF" in s]
    
    assert len(knows_rels) == 1
    assert len(works_for_rels) == 2
    assert len(produces_rels) == 1
    assert len(works_on_rels) == 2
    assert len(part_of_rels) == 1


def test_idempotency(complex_yaml_path):
    """Test that multiple conversions of the same file produce the same output."""
    converter = YAML2Cypher()
    
    # First conversion
    with tempfile.NamedTemporaryFile(suffix='.cypher', delete=False) as temp_file1:
        output_path1 = temp_file1.name
    
    # Second conversion
    with tempfile.NamedTemporaryFile(suffix='.cypher', delete=False) as temp_file2:
        output_path2 = temp_file2.name
    
    try:
        # Perform two separate conversions
        statements1 = converter.yaml_file_to_cypher(complex_yaml_path)
        converter.write_cypher_to_file(statements1, output_path1)
        
        statements2 = converter.yaml_file_to_cypher(complex_yaml_path)
        converter.write_cypher_to_file(statements2, output_path2)
        
        # Check that both output files have the same content
        assert filecmp.cmp(output_path1, output_path2)
    
    finally:
        # Clean up
        for path in [output_path1, output_path2]:
            if os.path.exists(path):
                os.unlink(path)