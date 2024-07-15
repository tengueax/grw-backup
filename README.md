# grw-backup

Ghost Recon Wildlands savefiles backup tool written in Python.

## Usage
```bash
usage: python main.py -i <input folder> -o <output folder> -t <steam/uplay>

GRW Backup Tool

options:
  -h, --help            show this help message and exit
  -t {steam,uplay,auto}, --type {steam,uplay,auto}
                        Game type. If you have a steam version of a game, use steam, uplay otherwise
  -o OUTPUT, --output OUTPUT
                        output folder path
  -i INTERVAL, --interval INTERVAL
                        interval in seconds
  -f FORMAT, --format FORMAT
                        timestamp format
```

## Example
```bash
python main.py -t steam -o ./grw_saves -i 300 -f "%Y-%m-%d_%H-%M-%S"
```