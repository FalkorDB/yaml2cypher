import pytest
import os
import sys
import tempfile
import yaml
from contextlib import contextmanager
from io import StringIO
from yaml2cypher import main


@contextmanager
def captured_output():
    """Capture stdout and stderr for testing."""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


@pytest.fixture
def sample_yaml_file():
    """Create a temporary YAML file for testing."""
    data = {
        "nodes": {
            "person1": {
                "labels": "Person",
                "name": "John Doe",
                "age": 30
            },
            "person2": {
                "labels": "Person",
                "name": "Jane Smith",
                "age": 28
            }
        },
        "relationships": [
            {
                "from": "person1",
                "to": "person2",
                "type": "KNOWS",
                "since": 2018
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w') as f:
        yaml.dump(data, f)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup after test
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_cli_default_output(sample_yaml_file):
    """Test CLI with default output filename."""
    expected_output = os.path.splitext(sample_yaml_file)[0] + '.cypher'
    
    # Delete the output file if it already exists
    if os.path.exists(expected_output):
        os.unlink(expected_output)
    
    try:
        with captured_output() as (out, err):
            exit_code = main([sample_yaml_file])
        
        # Check exit code and console output
        assert exit_code == 0
        assert f"Converted {sample_yaml_file} to {expected_output}" in out.getvalue()
        
        # Check that output file exists
        assert os.path.exists(expected_output)
        
        # Check file content
        with open(expected_output, 'r') as f:
            content = f.read()
            assert "CREATE (person1:Person" in content
            assert "CREATE (person2:Person" in content
            assert "CREATE (person1)-[:KNOWS" in content
    
    finally:
        # Clean up
        if os.path.exists(expected_output):
            os.unlink(expected_output)


def test_cli_custom_output(sample_yaml_file):
    """Test CLI with custom output filename."""
    with tempfile.NamedTemporaryFile(suffix='.cypher', delete=False) as temp_file:
        output_path = temp_file.name
    
    # Close and remove the temp file as we just want the name
    os.unlink(output_path)
    
    try:
        with captured_output() as (out, err):
            exit_code = main([sample_yaml_file, '-o', output_path])
        
        # Check exit code and console output
        assert exit_code == 0
        assert f"Converted {sample_yaml_file} to {output_path}" in out.getvalue()
        
        # Check that output file exists
        assert os.path.exists(output_path)
        
        # Check file content
        with open(output_path, 'r') as f:
            content = f.read()
            assert "CREATE (person1:Person" in content
            assert "CREATE (person2:Person" in content
            assert "CREATE (person1)-[:KNOWS" in content
    
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_cli_verbose_mode(sample_yaml_file):
    """Test CLI with verbose flag."""
    with tempfile.NamedTemporaryFile(suffix='.cypher', delete=False) as temp_file:
        output_path = temp_file.name
    
    # Close and remove the temp file as we just want the name
    os.unlink(output_path)
    
    try:
        with captured_output() as (out, err):
            exit_code = main([sample_yaml_file, '-o', output_path, '-v'])
        
        # Check exit code and console output
        assert exit_code == 0
        assert f"Converted {sample_yaml_file} to {output_path}" in out.getvalue()
        
        # Verbose mode should produce more output, but this is hard to test directly
        # as it depends on the logging implementation
    
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_cli_nonexistent_file():
    """Test CLI with a file that doesn't exist."""
    nonexistent_file = '/path/to/nonexistent/file.yaml'
    
    with captured_output() as (out, err):
        exit_code = main([nonexistent_file])
    
    # Should return non-zero exit code
    assert exit_code != 0
    
    # Should output an error message
    error_output = err.getvalue()
    assert "Error:" in error_output