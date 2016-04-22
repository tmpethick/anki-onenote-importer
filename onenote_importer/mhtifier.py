#!/usr/bin/env python3
# Encoding: UTF-8
"""mhtifier.py
Un/packs an MHT "archive" into/from separate files, writing/reading them in directories to match their Content-Location.

Uses part's Content-Location to name paths, or index.html for the root HTML.
Content types will be assigned according to registry of MIME types mapping to file name extensions.

History:
* 2013-01-11: renamed mhtifier.
* 2013-01-10: created mht2fs.py, and... done.
"""

# Standard library modules do the heavy lifting. Ours is all simple stuff.
import base64
import email
import email.message
import mimetypes
import os
import quopri
import sys
import argparse


def main():
    """Convert MHT file given as command line argument (or stdin?)
    to files and directories in the current directory.

    Usage:
        cd foo-unpacked/
        mht2fs.py ../foo.mht
    """
    parser = argparse.ArgumentParser(
        description="Extract MHT archive into new directory.")
    parser.add_argument(
        "mht", metavar="MHT",
        help='path to MHT file, use "-" for stdin/stdout.')
    # ??? How to make optional, default to current dir?
    parser.add_argument(
        "d", metavar="DIR",
        help="directory to create to store parts in, or read them from.")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()  # --help is built-in.

    # File name or stdin/stdout?
    if args.mht == "-":
        mht = sys.stdout if args.pack else sys.stdin.buffer
    else:
        if args.pack and os.path.exists(args.mht):
            # Refuse to overwrite MHT file.
            sys.stderr.write("Error: MHT file exists, won't overwrite.\n")
            sys.exit(-2)
        mht = open(args.mht, "wb" if args.pack else "rb")

    # New directory?
    if args.unpack:
        os.mkdir(args.d)

    # Change directory so paths (content-location) are relative to index.html.
    os.chdir(args.d)

    if not args.quiet:
        sys.stderr.write("Unpacking...\n")

    # Read entire MHT archive -- it's a multipart(/related) message.
    # Parser is "conducive to incremental parsing of email messages, such as
    # would be necessary when reading the text of an email message from a
    # source that can block", so I guess it's more efficient to have it read
    # stdin directly, rather than buffering.
    a = email.message_from_bytes(mht.read())

    # Save all parts to files.
    # walk() for a tree, but I'm guessing MHT is never nested?
    for p in a.get_payload():
        # ??? cs = p.get_charset() # Expecting "utf-8" for root HTML,
        # None for all other parts.
        # String coerced to lower case of the form maintype/subtype, else
        # get_default_type().
        ct = p.get_content_type()
        # File path. Expecting root HTML is only part with no location.
        fp = p.get("content-location") or "index.html"

        if args.verbose:
            sys.stderr.write("Writing %s to %s, %d bytes...\n" %
                             (ct, fp, len(p.get_payload())))

        # Create directories as necessary.
        if os.path.dirname(fp):
            os.makedirs(os.path.dirname(fp), exist_ok=True)

        # Save part's body to a file.
        open(fp, "wb").write(p.get_payload(decode=True))

    if not args.quiet:
        sys.stderr.write("Done.\nUnpacked %d files.\n" %
                         (len(a.get_payload())))

if __name__ == "__main__":
    main()  # Kindda useless if we're not using doctest or anything?
