# MarkMySAMM

A script that parses OWASP SAMM YAML source files and outputs Hugo markdown files for the OWASP SAMM website

## Usage

The script is designed to convert YAML files from a specified source directory into Markdown format for the SAMM website. To use the script, you would need to specify the input directory containing the YAML files and the output directory where the converted Markdown files will be saved.

Below is the general command line format to run the script:

```bash
python3 markmysamm.py -i <input_directory> -o <output_directory>
```

### Arguments

-i, --input (Required): This argument specifies the directory to scan for YAML files. Replace <input_directory> with the path to your directory containing the YAML files.

-o, --output (Required): This argument specifies the output directory where the Markdown files will be saved. Replace <output_directory> with the path to your desired output directory.
