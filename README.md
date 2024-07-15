# grw-backup

Ghost Recon Wildlands savefiles backup tool written in Python.

## Usage
```bash
usage: python main.py -i <input folder> -o <output folder> -t <steam/uplay>

GRW Backup Tool

options:
  -h, --help            show this help message and exit
  -t {auto,steam,uplay}, --type {auto,steam,uplay}
                        Game type (Defaults to 'auto')
  -o OUTPUT, --output OUTPUT
                        Output folder path (Defaults to './saves')
  -i INTERVAL, --interval INTERVAL
                        Backup interval in seconds (Defaults to 300 sec.)
  -f FORMAT, --format FORMAT
                        Backup folder format (Defaults to '%d.%m.%Y_%H-%M-%S')
```

## Example
```bash
python main.py -t steam -o ./grw_saves -i 300 -f "%Y-%m-%d_%H-%M-%S"
```