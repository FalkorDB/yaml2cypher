import yaml
from typing import Dict, List, Any, Optional

from yaml2cypher.utils import setup_logger


class YAML2Cypher:
    """Convert YAML files to Cypher queries for graph databases."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the converter with optional configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = setup_logger("yaml2cypher")

    def load_yaml(self, yaml_file: str) -> Dict[str, Any]:
        """Load YAML file and return the parsed content.

        Args:
            yaml_file: Path to the YAML file

        Returns:
            Parsed YAML content as dictionary

        Raises:
            Exception: If the file cannot be read or parsed
        """
        try:
            with open(yaml_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading YAML file {yaml_file}: {e}")
            raise

    def _format_property_value(self, value: Any) -> str:
        """Format a property value for Cypher query.

        Args:
            value: The property value to format

        Returns:
            Formatted value as a string for Cypher
        """
        if isinstance(value, str):
            # Escape quotes and return as string
            escaped_value = value.replace("'", "\\'")
            return f"'{escaped_value}'"
        elif value is None:
            return "null"
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            # Format lists as Cypher arrays
            items = [self._format_property_value(item) for item in value]
            return f"[{', '.join(items)}]"
        elif isinstance(value, dict):
            # Format dictionaries as Cypher maps
            props = [f"{k}: {self._format_property_value(v)}" for k, v in value.items()]
            return f"{{{', '.join(props)}}}"
        else:
            # Default stringification for other types
            return f"'{str(value)}'"

    def _generate_node_properties(self, properties: Dict[str, Any]) -> str:
        """Generate Cypher node properties string.

        Args:
            properties: Dictionary of node properties

        Returns:
            Formatted properties string for Cypher
        """
        if not properties:
            return ""

        props = []
        for key, value in properties.items():
            formatted_value = self._format_property_value(value)
            props.append(f"{key}: {formatted_value}")

        return f"{{{', '.join(props)}}}"

    def _convert_node(self, node_id: str, node_data: Dict[str, Any]) -> str:
        """Convert a node definition to Cypher CREATE statement.

        Args:
            node_id: Identifier for the node
            node_data: Node data including labels and properties

        Returns:
            Cypher CREATE statement for the node
        """
        # Extract node labels and properties
        labels = node_data.get('labels', [])
        if isinstance(labels, str):
            labels = [labels]

        # Format node labels
        label_str = ''.join([f":{label}" for label in labels])

        # Extract and format node properties
        properties = {k: v for k, v in node_data.items() if k != 'labels'}
        prop_str = self._generate_node_properties(properties)

        # Generate Cypher CREATE statement
        return f"CREATE ({node_id}{label_str} {prop_str})"

    def _convert_relationship(self, rel_data: Dict[str, Any]) -> str:
        """Convert a relationship definition to Cypher CREATE statement.

        Args:
            rel_data: Relationship data including from, to, type and properties

        Returns:
            Cypher CREATE statement for the relationship
        """
        from_node = rel_data.get('from')
        to_node = rel_data.get('to')
        rel_type = rel_data.get('type')

        if not all([from_node, to_node, rel_type]):
            self.logger.error(f"Relationship missing required fields: {rel_data}")
            return ""

        # Extract and format relationship properties
        properties = {k: v for k, v in rel_data.items() if k not in ['from', 'to', 'type']}
        prop_str = self._generate_node_properties(properties)

        # Generate Cypher CREATE statement for relationship
        return f"CREATE ({from_node})-[:{rel_type} {prop_str}]->({to_node})"

    def convert_yaml_to_cypher(self, yaml_data: Dict[str, Any]) -> List[str]:
        """Convert parsed YAML data to Cypher queries.

        Args:
            yaml_data: Parsed YAML data

        Returns:
            List of Cypher statements
        """
        cypher_statements = []

        # Process nodes section
        nodes = yaml_data.get('nodes', {})
        for node_id, node_data in nodes.items():
            cypher_statements.append(self._convert_node(node_id, node_data))

        # Process relationships section
        relationships = yaml_data.get('relationships', [])
        for rel_data in relationships:
            cypher_statements.append(self._convert_relationship(rel_data))

        return cypher_statements

    def yaml_file_to_cypher(self, yaml_file: str) -> List[str]:
        """Convert a YAML file to Cypher queries.

        Args:
            yaml_file: Path to the YAML file

        Returns:
            List of Cypher statements
        """
        yaml_data = self.load_yaml(yaml_file)
        return self.convert_yaml_to_cypher(yaml_data)

    def write_cypher_to_file(self, cypher_statements: List[str], output_file: str) -> None:
        """Write Cypher statements to a file.

        Args:
            cypher_statements: List of Cypher statements
            output_file: Path to the output file

        Raises:
            Exception: If the file cannot be written
        """
        try:
            with open(output_file, 'w') as f:
                for statement in cypher_statements:
                    f.write(f"{statement};\n")
            self.logger.info(f"Cypher queries written to {output_file}")
        except Exception as e:
            self.logger.error(f"Error writing Cypher to file {output_file}: {e}")
            raise
