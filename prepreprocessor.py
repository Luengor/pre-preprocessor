#!/usr/bin/env python3
## Imports
from typing import Tuple 
from sys import argv
from enum import Enum
import os
import re

## Constants
TEXTS = {
    "usage": "Usage: {0} <input> [output]",
}

class error_code (Enum):
    OK = 0
    INVALID_ARGS = 1
    FILE_DOESNT_EXIST = 2
    MISSING_INCLUDE = 3

# Does the actual prepreprocessing'==>
def prepreprocess(file:str, filepath:str) -> Tuple[error_code, str]:
    needed = re.findall(r"#include[ ]*\"(.+)\"", file, re.MULTILINE)

    search_paths = [filepath]
    cpath = os.getenv("CPATH")
    if cpath != None:
        search_paths += cpath.split(':')

    # Check if the needed files (and the sources) exists (and get them) 
    files = {} 
    for header_file in needed:
        source_file = header_file.replace('.h', '.c') 

        # Search for file
        for spath in search_paths:
            full_header_file = os.path.join(spath, header_file)
            full_source_file = os.path.join(spath, source_file)

            if (os.path.exists(full_header_file) and
                    os.path.exists(full_source_file)):
                # Load them
                files[header_file] = {} 
                with open(full_header_file, 'r') as f:
                    files[header_file]["header"] = f.read()
                with open(full_source_file, 'r') as f:
                    files[header_file]["source"] = f.read()

                # Exit
                break;

        # Check if files have been found
        if header_file not in files.keys():
            return (error_code.MISSING_INCLUDE, '')

    # They exist, do the replacement
    for headername, files in files.items():
        # "Import" the header
        header = files["header"]
        status, clean_header = prepreprocess(header, os.path.dirname(headername));
        if status != error_code.OK:
            return (status, '')

        file = re.sub(rf'(#include[ ]*\"{headername}\")',
                      lambda _: f"///Start of {headername}\n{clean_header}\n///End of {headername}\n" , file) 

        # Dont re-include the file 
        source = files["source"]
        headername_real = headername.split('/')[-1]

        clean_source = re.sub(rf'#(include[ ]*\"{headername_real}\")[ ]*', r'// \1', source)
        status, clean_source = prepreprocess(clean_source, os.path.dirname(headername));
        if status != error_code.OK:
            return (status, '')

        file += f"/// Start of {headername} source\n"
        file += clean_source 
        file += f"/// End of {headername} source\n"

        


    # Return the file
    return (error_code.OK, file);
# <=='

if __name__ == "__main__":
    # Check args
    if (len(argv) not in (2, 3)):
        print(TEXTS["usage"].format(argv[0]))
        exit(error_code.INVALID_ARGS.value)

    # Check if main file exists
    if not os.path.exists(argv[1]):
        exit(error_code.FILE_DOESNT_EXIST.value)

    # Run over the file, noting the files needed
    with open(argv[1], 'r') as f:
        file = f.read()

    status, file = prepreprocess(file, os.path.dirname(argv[1]))

    if not status == error_code.OK:
        print(f"no ({status})")
        exit(status.value)

    # Write file
    if len(argv) == 2:
        print(file)
    else:
        with open(argv[2], "w") as f:
            f.write(file)

