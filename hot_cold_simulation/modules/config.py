import configparser
from pathlib import Path
from typing import Any


def get_config_properties(file_name: str) -> dict[str, dict[str, str]] | Any:
    """Return the variables found in a user specified .ini file in the configurations folder.

    Args:
        file_name (str): Name of the configuration file found in the config folder. Note, file type suffix is
        not required to pass in.  By default we only accept .ini files.

    Returns:
        Dict[str, Any]: Dictionary of the sections and items in the configuration file.
    """
    # Create configparser object and read in the configuration file.
    config = configparser.ConfigParser()
    config.read(Path(CONFIG_DIR).joinpath(f"{file_name}.ini"))

    # Convert config parser object into a dictionary. First level dictionary key is the section name
    # and the second level dictionary are the section key names.
    return config.__dict__["_sections"]


def get_package_root() -> str:
    """Grab the root directory of this package.

    NOTE, this variable is relatively referenced. If this file is moved, path's that depend on this
    method will generate the incorrect path.

    Returns:
        str: Root path of this project represented as a string
    """
    return Path(__file__).parent.parent.as_posix()


def get_project_root() -> str:
    """Grab the root directory of this project.

    NOTE, this variable is relatively referenced. If this file is moved, path's that depend on this
    method will generate the incorrect path.

    Returns:
        str: Root path of this project represented as a string
    """
    return Path(__file__).parent.parent.parent.as_posix()


def build_directory_path(input_path: str) -> str:
    """Construct an absolute path from a string and create a directory at the given path if it does not exist.

    This method also takes care of checking if the string representation of `input_path` is an absolute
    or relative path. Relative paths are resolved based on the current working directory. See examples below.

    Absolute: `c:/path/to/directory` -> `C:/path/to/directory`

    Relative: `../../directory` -> `C:/directory` when CWD = `C:/path/to/directory`

    Relative: `directory/example` -> `C:/path/to/directory/example` when CWD = `C:/path/to/directory`

    Args:
        input_path (str): String that represents a relative or absolute path

    Returns:
        str: Return the string representation of path
    """

    # Create a Path object from the user input
    directory_path = Path(input_path)

    # Check if path is absolute
    if not directory_path.is_absolute():
        # If the path is relative, make it relative to the current directory
        current_dir = Path.cwd()
        directory_path = (Path(current_dir) / directory_path).resolve()

    # Ensure path exists and return as a string
    directory_path.mkdir(exist_ok=True, parents=True)
    return directory_path.as_posix()


# Grab folder paths to referenced directories and files.
PACAKGE_DIR = get_package_root()
ROOT_DIR = get_project_root()
CONFIG_DIR = Path(ROOT_DIR).joinpath("config")
DATA_DIR = Path(ROOT_DIR).joinpath("data")

# Create directories for output results
ANIMATION_DIR = Path(build_directory_path(input_path="animation"))
MONTE_CARLO_LOG_DIR = Path(build_directory_path(input_path="monte_carlo_results"))
