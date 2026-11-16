# Running the product

- Machine: any machine with Python 3.8 or later. Nothing to install.
- Start: there is no server; each run is one command, `bin/wordcount <file>`,
  `bin/wordcount --lines <file>` or `bin/wordcount --url <address>`. It prints one number and exits.
- Stop: nothing to stop.
- Interfaces: the `bin/wordcount` command only.
- Starting state: write the input file anywhere outside the repository, such as a folder made with
  `mktemp -d`.
- Web pages: start the page stand-in with `sh tools/page-server.sh`; it serves the test pages,
  such as `/hello`, on `http://localhost:8765`, and is stopped with Ctrl-C.
- Safe to touch: files you create outside the repository, and the page stand-in started by
  `tools/page-server.sh`.
- Never to be touched: any other web server or web address, including one you start yourself, and
  anything on the internet.
