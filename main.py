import re
import time
import shutil
import logging
import enum
from pathlib import Path
from argparse import ArgumentParser, Namespace

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s (%(levelname)s) %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs.txt"),
    ],
)
logger = logging.getLogger(__name__)

DEFAULT_INTERVAL = 60 * 5
DEFAULT_FOLDER_FORMAT = "%d.%m.%Y_%H-%M-%S"
UBISOFT_SAVEGAMES_PATH = Path(
    "C:/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/savegames/"
)


class GameType(enum.StrEnum):
    """Game type"""

    AUTO = "auto"
    STEAM = "steam"
    UPLAY = "uplay"


def get_ubisoft_account_folder() -> Path:
    """Get Ubisoft account folder path

    :return: Path to the Ubisoft account folder
    """
    base_path = UBISOFT_SAVEGAMES_PATH

    if not base_path.is_dir():
        raise ValueError(f"'{base_path}' is not a directory")

    for item in base_path.iterdir():
        if not item.is_dir():
            continue

        # Skip if not a valid Ubisoft account folder (must be a UUID).
        if not re.match(
            r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
            item.name,
        ):
            continue

        return item

    raise ValueError(f"No Ubisoft account folder found in '{base_path}'")


def get_game_type(account_folder: Path) -> GameType:
    """Get game type

    :param account_folder: Account folder
    :return: Game type
    """
    if (account_folder / "1771").is_dir():
        return GameType.UPLAY

    if (account_folder / "3559").is_dir():
        return GameType.STEAM

    raise ValueError(f"No GRW saves folder found in '{account_folder}'")


def get_wildlands_saves_folder(game_type: GameType) -> Path:
    """Get Ghost Recon Wildlands saves folder path.

    :param game_type: Game type. If you have a steam version of a game, use steam, uplay otherwise
    :return: Path to the saves folder
    """
    account_folder = get_ubisoft_account_folder()

    match game_type:
        case GameType.AUTO:
            saves_path = account_folder / (
                "1771" if (account_folder / "1771").is_dir() else "3559"
            )
        case GameType.STEAM:
            saves_path = account_folder / "3559"
        case GameType.UPLAY:
            saves_path = account_folder / "1771"
        case _:
            raise ValueError(f"Invalid game type '{game_type}'")

    if not saves_path.is_dir():
        raise ValueError(f"'{saves_path}' is not a directory")

    return saves_path


def parse_args() -> Namespace:
    """Parse command line arguments

    :return: Parsed arguments
    """
    parser = ArgumentParser(
        description="GRW Backup Tool",
        usage="python main.py -i <input folder> -o <output folder> -t <steam/uplay>",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=list(map(str, GameType)),
        default=GameType.AUTO.value,
        help="Game type. Defaults to 'auto'",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path.cwd() / "saves",
        help="output folder path",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help="interval in seconds",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default=DEFAULT_FOLDER_FORMAT,
        help="timestamp format",
    )
    return parser.parse_args()


def init_output_folder(output_folder: Path) -> None:
    """Initialize output folder

    :param output_folder: Output folder
    """
    if not output_folder.is_dir():
        logger.debug(f"Creating output folder at '{output_folder}'")
        output_folder.mkdir(parents=True)
    else:
        logger.debug(f"Using existing output folder at '{output_folder}'")


def main():
    args = parse_args()

    logging.debug(f"Ubisoft savegames folder: '{UBISOFT_SAVEGAMES_PATH}'")

    # Resolving paths
    account_folder = get_ubisoft_account_folder()
    saves_folder = get_wildlands_saves_folder(args.type)
    logging.debug(f"Ubisoft account folder: '{account_folder}'")
    logging.debug(
        f"Wildlands saves folder: '{saves_folder}' ({get_game_type(account_folder).title()})"
    )

    # Initializing output folder
    output_folder: Path = args.output.resolve()  # type: ignore
    init_output_folder(output_folder)

    logger.info("Backup delay: %d sec.", args.interval)

    # Starting backup loop
    try:
        while True:
            has_saves = False

            destination_folder = output_folder / time.strftime(args.format)
            if not destination_folder.is_dir():
                logger.debug(f"Creating backup folder '{destination_folder}'")
                destination_folder.mkdir()

            for file in saves_folder.iterdir():
                if file.is_file():
                    has_saves = True
                    logger.debug(f"Copying '{file}' to '{destination_folder}'")
                    shutil.copy(file, destination_folder)

            if not has_saves:
                logger.debug("No saves found")
                destination_folder.rmdir()

            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")


if __name__ == "__main__":
    main()
