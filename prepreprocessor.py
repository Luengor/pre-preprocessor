#!/usr/bin/env python3
## Imports
from sys import argv
from enum import Enum
import os
import re

## Constants
TEXTS = {
    "usage": "Usage: {0} <input> <output>".format(argv[0]),
    "noinput": "Input file {0} does not exist.".format(argv[1]),
    "missing_include": "Include file {0} is missing or lacks source",
    "help": ""
}

class ERROR_CODES (Enum):
    OK = 0
    INVALID_ARGS = 1
    FILE_DOESNT_EXIST = 2
    MISSING_INCLUDE = 3



if __name__ == "__main__":
    # Check args
    if (len(argv) != 3):
        print(TEXTS["usage"])
        exit(ERROR_CODES.INVALID_ARGS.value)

    if not os.path.exists(argv[1]):
        print(TEXTS["noinput"])
        exit(ERROR_CODES.FILE_DOESNT_EXIST.value)

    
    # Run over the file, noting the files needed
    with open(argv[1], 'r') as f:
        file = f.read()
    needed = re.findall(r"#include[ ]*\"(.+)\"", file, re.MULTILINE)

    # Check if the needed files (and the sources) exists (and get them) 
    files = {} 
    for header_file in needed:
        source_file = header_file.replace('.h', '.c') 

        # Check if files exits
        if (not os.path.exists(header_file) or \
                not os.path.exists(source_file)):
            print(TEXTS["missing_include"].format(header_file))
            exit(ERROR_CODES.MISSING_INCLUDE.value)

        # Load files
        files[header_file] = {} 
        with open(header_file) as f:
            files[header_file]["header"] = f.read()
        with open(source_file) as f:
            files[header_file]["source"] = f.read()

    # They exist, do the replacement
    for headername, files in files.items():
        # "Import" the header
        header = files["header"]
        file = re.sub(rf'(#include[ ]*\"{headername}\")',
                      rf"///Start of {headername}\n{header}\n///End of {headername}\n", file) 

        # Take any includes "" out for now
        source = files["source"]
        file += f"/// Start of {headername} source\n"
        file += re.sub(rf'(#include[ ]*\".+\")[ ]*\n', r'// \1', source)
        file += f"/// End of {headername} source\n"

    # Write file
    with open(argv[2], "w") as f:
        f.write(file)

