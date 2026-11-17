"""Command line: stockroom add <item> <count>, stockroom show."""

import sys

from stockroom.logs import configure, get_logger

STOCK: dict[str, int] = {}


def main() -> int:
    configure()
    log = get_logger(__name__)
    args = sys.argv[1:]
    if args[:1] == ["add"] and len(args) == 3:
        STOCK[args[1]] = STOCK.get(args[1], 0) + int(args[2])
        log.info("stock_added", item=args[1], count=int(args[2]))
        return 0
    if args == ["show"]:
        for item, count in sorted(STOCK.items()):
            print(f"{item}\t{count}")
        return 0
    log.warning("bad_arguments", args=args)
    print("usage: stockroom add <item> <count> | stockroom show", file=sys.stderr)
    return 2
