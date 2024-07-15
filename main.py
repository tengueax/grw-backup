import time
import shutil
import logging
from pathlib import Path
from argparse import ArgumentParser

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
WILDLANDS_SAVEGAMES_PATH = Path(
    "C:/Program Files (x86)/Ubisoft/Ubisoft Game Launcher/savegames/"
)


def get_saves_folder(game_type: str) -> Path:
    base_path = WILDLANDS_SAVEGAMES_PATH

    if not base_path.is_dir():
        raise ValueError(f"'{base_path}' is not a directory")

    account_id = base_path.walk()
    folders = next(account_id)[1]
    if len(folders) == 0:
        raise ValueError(f"No folders found in '{base_path}'")

    account_id = folders[0]
    account_folder = base_path / account_id

    if game_type == "auto":
        game_type = "uplay" if (account_folder / "1771").is_dir() else "steam"

    if game_type == "steam":
        saves_path = account_folder / "3559"
    elif game_type == "uplay":
        saves_path = account_folder / "1771"
    else:
        raise ValueError(f"Invalid game type '{game_type}'")

    if not saves_path.is_dir():
        raise ValueError(f"'{saves_path}' is not a directory")

    return saves_path


def main():
    parser = ArgumentParser(
        description="GRW Save",
        usage="python main.py -i <input folder> -o <output folder> -t <steam/uplay>",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["steam", "uplay", "auto"],
        default="auto",
        help="Game type. If you have a steam version of a game, use steam, uplay otherwise",
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
    args = parser.parse_args()

    output_folder: Path = args.output.resolve()
    if not output_folder.is_dir():
        logger.debug(f"Creating output folder at '{output_folder}'")
        output_folder.mkdir(parents=True)
    else:
        logger.debug(f"Using existing output folder at '{output_folder}'")

    saves_folder = get_saves_folder(args.type)
    logging.debug(f"Saves folder for '{args.type}' is '{saves_folder}'")

    logger.debug(f"Saving files from '{saves_folder}' to '{output_folder}'")

    logger.info("Copying files every %d seconds", args.interval)

    try:
        while True:
            timestamp = time.strftime(args.format)
            destination_folder = output_folder / timestamp
            if not destination_folder.is_dir():
                logger.debug(f"Creating folder '{destination_folder}'")
                destination_folder.mkdir()

            for file in saves_folder.iterdir():
                if file.is_file():
                    logger.debug(f"Copying '{file}' to '{destination_folder}'")
                    shutil.copy(file, destination_folder)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")


if __name__ == "__main__":
    main()
