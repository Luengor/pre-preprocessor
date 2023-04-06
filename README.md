# I hate 1 file restrictions
The idea is simple:
* You have your c file with the needed libraries included.
* You have a 1 file restriction.
* The script replaces the imports with the headers and appends the code at the
  end (yes, this is just a static linker)

## How
The script searches in the imports and replaces every `import "something.h"`
with the contents of the file `something.h`. If its not found, it also 
searches in `CPATH`.  

## Usage
```sh
python3 prepreprocessor.py input_file output_file
```

