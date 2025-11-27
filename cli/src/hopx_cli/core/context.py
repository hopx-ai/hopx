"""CLI context and runtime state management.

Provides context object that holds runtime state for commands including
output format, verbosity, and other session-specific settings.
"""

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .config import CLIConfig


class OutputFormat(str, Enum):
    """Output format options for CLI commands.

    Attributes:
        TABLE: Rich formatted tables with colors and borders
        JSON: Machine-readable JSON output
        PLAIN: Plain text output suitable for scripting
    """

    TABLE = "table"
    JSON = "json"
    PLAIN = "plain"


class CLIContext:
    """Runtime context for CLI commands.

    Holds session-specific state including configuration, output format,
    verbosity level, and other runtime settings.

    Attributes:
        config: CLI configuration instance
        output_format: Current output format for commands
        verbose: Enable verbose output
        quiet: Suppress non-essential output
        no_color: Disable color output (respects NO_COLOR env var)
    """

    def __init__(
        self,
        config: "CLIConfig | None" = None,
        output_format: OutputFormat | None = None,
        verbose: bool = False,
        quiet: bool = False,
        no_color: bool = False,
    ) -> None:
        """Initialize CLI context.

        Args:
            config: CLI configuration instance. Loads default if not provided.
            output_format: Output format. Uses config default if not provided.
            verbose: Enable verbose output
            quiet: Suppress non-essential output
            no_color: Disable color output
        """
        if config is None:
            # Lazy import to avoid circular dependencies during testing
            from .config import CLIConfig

            config = CLIConfig.load()

        self.config = config
        self.output_format = output_format or OutputFormat(self.config.output_format)
        self.verbose = verbose
        self.quiet = quiet
        self.no_color = no_color

        # Additional runtime state
        self._state: dict[str, Any] = {}

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get runtime state value.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set runtime state value.

        Args:
            key: State key
            value: State value
        """
        self._state[key] = value

    def is_json_output(self) -> bool:
        """Check if output format is JSON.

        Returns:
            True if JSON format is selected
        """
        return self.output_format == OutputFormat.JSON

    def is_plain_output(self) -> bool:
        """Check if output format is plain text.

        Returns:
            True if plain text format is selected
        """
        return self.output_format == OutputFormat.PLAIN

    def is_table_output(self) -> bool:
        """Check if output format is table.

        Returns:
            True if table format is selected
        """
        return self.output_format == OutputFormat.TABLE
