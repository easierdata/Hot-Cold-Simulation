import argparse
import sys
from pathlib import Path
from typing import Any

from modules.config import CONFIG_DIR  # type: ignore
from modules.defaults import default_configurations  # type: ignore


# Function to create or update a single .env file
def check_configuration(
    variables: dict[str, Any], configuration_name: str, args: argparse.Namespace
) -> None:
    """Method containing various checks to ensure that validity of a configuration file. The functionality
    includes checking for any missing variables and resetting variables to their default values.

    Args:
        variables (dict[str, Any]): A dictionary containing one or more parameter name/parameter value pairs.
        configuration_name (str): Name of the configuration file to be checked.
        args (argparse.Namespace): Namespace object containing the parsed command-line attributes.
    """
    # Ensure configuration direction exists
    CONFIG_DIR.mkdir(exist_ok=True, parents=True)

    # Instantiate the configuration file path
    configuration_file = CONFIG_DIR / f"{configuration_name}.env"

    # check if the file already exists before making any modifications.
    if not configuration_file.exists():
        generate_new_config_file(variables, configuration_file)
    else:
        checked_lines = check_for_missing_variables(variables, configuration_file)
        write_to_file(configuration_file, checked_lines)

    # After we account for any missing variables in the configuration files, we can perform either of the reset options
    if args.hard_reset:
        update_existing_variables(variables, configuration_file)
    elif args.reset:
        non_empty_variables = {k: v for k, v in variables.items() if v}
        update_existing_variables(non_empty_variables, configuration_file)


def check_for_missing_variables(
    variables: dict[str, Any], config_file: Path
) -> list[str]:
    """Method to check for any missing variables in the configuration file.

    Args:
        variables (dict[str, Any]): A dictionary containing one or more parameter name/parameter value pairs.
        config_file (Path): Configuration file path.

    Returns:
        list[str]: A list
    """
    # Read in each line from the file.
    with config_file.open("r") as file:
        lines = file.readlines()

        # Check for any missing variables in the file
        for var_name, var_value in variables.items():
            if not variable_exists(var_name, lines):
                append_variable(var_name, var_value, lines)
    return lines


def variable_exists(variable_name: str, lines: list[str]) -> bool:
    x = any(line.startswith(f"{variable_name}=") for line in lines)
    print(x)
    return x


def append_variable(var_name: str, var_value: str, lines: list[str]) -> None:
    """Append a single key/value pair to a list of variables.

    Args:
        var_name (str): Configuration variable name
        var_value (str): Configuration variable value
        lines (list[str]): List of lines from the configuration file.
    """
    if var_value is not None:
        lines.append(f"{var_name}={var_value}\n")
    else:
        lines.append(f"{var_name}=\n")


def update_existing_variables(variables: dict[str, Any], config_file: Path) -> None:
    """Update existing variables in a configuration file.

    Args:
        variables (dict[str, Any]): A dictionary containing one or more parameter name/parameter value pairs.
        config_file (Path): Configuration file path.
    """
    # Read in each line from the file.
    with config_file.open("r") as file:
        lines = file.readlines()

    # Loop through each line in the file and modify the values based on the configuration defaults.
    for i, line in enumerate(lines):
        for var_name, var_value in variables.items():
            if var_name in line:
                # Account for variables with empty defaults.
                if var_value is not None:
                    lines[i] = f"{var_name}={var_value}\n"
                else:
                    lines[i] = f"{var_name}=\n"
    write_to_file(config_file, lines)


def write_to_file(config_file: Path, lines: list[str]) -> None:
    """Write to a configuration file a list of key/value pairs.

    Args:
        config_file (Path): Configuration file path.
        lines (list[str]): List of lines from the configuration file.
    """
    with config_file.open("w") as file:
        file.writelines(sorted(lines))


def generate_new_config_file(variables: dict[str, Any], config_file: Path) -> None:
    """Generate a file containing environment variables that the project references.

    NOTE: Fill will be overwritten if it already exists.

    Args:
        variables (dict[str, Any]): A dictionary containing one or more parameter name/parameter value pairs.
        env_file (Path): Path object representing the file path.
    """
    with config_file.open("w") as file:
        for var_name, var_value in variables.items():
            if var_value is not None:
                file.write(f"{var_name}={var_value}\n")
            else:
                file.write(f"{var_name}=\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate, update or reset configuration files that your project uses"
    )
    parser.add_argument(
        "--reset",
        dest="reset",
        action="store_true",
        help="Reset non-empty variables to their default values",
    )
    parser.add_argument(
        "--hard-reset",
        dest="hard-reset",
        action="store_true",
        help="Reset all variables to their default values",
    )
    parser.add_argument(
        "--config-name",
        dest="config_name",
        type=str,
        required=False,
        help="Name of the output .env file",
    )

    args = parser.parse_args()

    # Check if the selected dictionary configuration exists.
    if args.config_name:
        if args.config_name not in list(default_configurations.keys()):
            print(
                f"The configuration you specified does not exist. Please select from the following: {list(default_configurations.keys())}"
            )
            sys.exit()
        else:
            check_configuration(
                default_configurations[args.config_name],
                args.config_name,
                args,
            )
    # if user did not call for a specific configuration, generate files for all configurations.
    else:
        for config_name, variables in default_configurations.items():
            check_configuration(variables, config_name, args)

    print(f'.env files have been generated or updated in the "{CONFIG_DIR}" directory.')
    print("You can open them and manually update the values as needed.")


if __name__ == "__main__":
    main()