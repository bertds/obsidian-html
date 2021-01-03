from .config import GLOBAL
import sys
import argparse
from .Vault import Vault
from .Note import Note

def main():
    parser = argparse.ArgumentParser(
        prog="obsidian-html",
        description="Converts an Obsidian vault into HTML")

    parser.add_argument("Vault",
                        metavar="vault",
                        type=str,
                        help="Path to the vault root")

    parser.add_argument("-o", "--output_dir",
                        default="./html",
                        help="Path to place the generated HTML")

    parser.add_argument("-t", "--template",
                        default=None,
                        help="Path to HTML template")

    parser.add_argument("-d", "--dirs",
                        nargs="+",
                        default=[],
                        help="Extra sub-directories in vault that you want included")

    parser.add_argument("-f", "--filter",
                        nargs="+",
                        default=[],
                        help="Filter notes by tags")
    
    parser.add_argument("-e", "--extensions",
                        action="store_true",
                        help="Whether to include a '.html' extension on links. Useful for viewing locally.")

    args = parser.parse_args()

    GLOBAL.HTML_LINK_EXTENSIONS = args.extensions
    vault = Vault(args.Vault, extra_folders=args.dirs, html_template=args.template, filter=args.filter)
    vault.export_html(args.output_dir)
    print('start copy')
    vault.copy_media(args.output_dir)
