import sys


def count(text):
    return len(text.split())


if __name__ == "__main__":
    print(count(sys.stdin.read()))
