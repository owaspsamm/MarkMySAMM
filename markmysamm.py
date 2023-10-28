import os
import yaml
import argparse
from collections import defaultdict
import pprint
import re
from unidecode import unidecode

# The above imports require these libraries
# pip install unidecode
# pip install pyyaml

pp = pprint.PrettyPrinter(indent=4)

# Returns a new defaultdict(nested_dict) when called.
# This is a recursive data structure that produces a new nested dictionary each time a key is accessed that does not yet exist.
def create_nested_dict():
    return defaultdict(create_nested_dict)

# Reads a YAML file and return a dictionary of its contents.
# If the file cannot be parsed as YAML, it prints an error message and returns None.
def read_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)

# Recursively scans a directory and all of its subdirectories.
# If it encounters a file that ends with '.yaml' or '.yml', it reads that file and adds its contents to the dictionary.
# If it encounters a directory, it recursively scans that directory.
def scan_directory(path, parent_dict):
    for entry in os.scandir(path):
        if entry.is_file() and (entry.name.endswith('.yaml') or entry.name.endswith('.yml')):
            parent_dict[remove_yaml_extension(entry.name)] = read_yaml(entry.path)
        elif entry.is_dir():
            scan_directory(entry.path, parent_dict[entry.name])

def remove_yaml_extension(file_name):
    """
    This function takes a file name as an argument. If the file name ends with 
    '.yaml' or '.yml', it removes that extension and returns the file name without 
    it. If the file name does not end with '.yaml' or '.yml', it returns the 
    file name unchanged.

    :param file_name: String, name of the file
    :return: String, file name without '.yaml' or '.yml' extension if it exists
    """
    if file_name.endswith('.yaml'):
        return file_name[:-5]  # Removing '.yaml'
    elif file_name.endswith('.yml'):
        return file_name[:-4]  # Removing '.yml'
    else:
        return file_name  # Return the original file name if no yaml extension
    
def ensure_directory_exists(directory):
    """
    Ensure that a directory exists.
    If the directory does not exist, create it.
    
    :param directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_template_content(input_file, variables):
    """
    Reads a Markdown template file, replaces placeholders with actual values, and returns content.

    :param input_file: path to the input template file
    :param variables: a dictionary where keys are placeholder names and values are the actual values
    """
    with open(input_file, 'r') as file:
        template = file.read()
    
    return template.format(**variables)


def process_template(input_file, output_file, variables):
    """
    Reads a Markdown template file, replaces placeholders with actual values, and writes to a new file.

    :param input_file: path to the input template file
    :param output_file: path to the output file
    :param variables: a dictionary where keys are placeholder names and values are the actual values
    """
    print('[+] Writing file: '+output_file)
    content = process_template_content(input_file, variables)
    
    with open(output_file, 'w+') as file:
        file.write(content)

def name_to_slug(input_string):
    """
    This function takes a string, converts it to lowercase, removes all special characters except for whitespace, 
    and replaces whitespace with hyphens.

    :param input_string: String, the string to process
    :return: String, processed string
    """
    # Remove accents
    ascii_string = unidecode(input_string)
    # Convert string to lowercase
    lower_string = ascii_string.lower()
    # Replace & with 'and'
    and_string = re.sub(r'&', 'and', lower_string)
    # Remove all special characters except for whitespace using regular expressions
    alphanumeric_whitespace_string = re.sub(r'[^a-zA-Z0-9\s]', '', and_string)
    # Replace whitespace with hyphens
    hyphenated_string = re.sub(r'\s+', '-', alphanumeric_whitespace_string)
    return hyphenated_string

# Sets up command line argument parsing.
def parse_arguments():
    parser = argparse.ArgumentParser(description='Read SAMM source directory containing YAML files and output Markdown for SAMM website')
    parser.add_argument('-i', '--input', type=str, help='Directory to scan', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output directory', required=True)
    return parser.parse_args()

# Takes a practice level ID from an activity and retreives the level integer (1, 2 or 3)
def levelid_to_level(nested_dict,level_id):
    # Find the matching practice level
    for plvkey,plvvalue in nested_dict['practice_levels'].items():
        if plvvalue['id'] == level_id:
            # Now find the matching maturity level for this practice level
            for mlvkey,mlvvalue in nested_dict['maturity_levels'].items():
                if mlvvalue['id'] == plvvalue['maturitylevel']:
                    # Return the level number
                    return mlvvalue['number']
                
def fix_indent(text, tab_count=1):
    # Replace each tab count with the appropriate number of spaces
    indentation = ' ' * (4 * tab_count)
    # Replace each linebreak with a linebreak followed by the specified indentation
    indented_text = text.replace('\n', '\n' + indentation)
    return indented_text

def fix_bool(variable):
    if isinstance(variable, bool):
        return 'Yes' if variable else 'No'
    else:
        return variable
                
# Main script.
# It parses command line arguments, creates a new nested dictionary,
# then scans the directory provided by the command line argument and prints the resulting dictionary.
if __name__ == "__main__":
    # Parse command line args
    args = parse_arguments()
    # Create a nested dictionary containing directory structure and YAML file contents
    nested_dict = create_nested_dict() 
    scan_directory(args.input, nested_dict)
    # Print nested dictionary (REMOVE)
    #pp.pprint(dict(nested_dict))

    '''
    WRITE BUSINESS FUNCTION FILES
    '''

    # Make sure the output directory for business functions exists, create it if not
    ensure_directory_exists(args.output)
    # Loop through each business function
    for bfkey,bfvalue in nested_dict['business_functions'].items():
        print('[+] Business function: '+bfvalue['name'])
        # Inside the business function page, we need to list all child security practices
        # Get a list of associated security practices and their URLs
        # Create empty lists for the results, and loop through security practices
        practices = []
        urls = []
        for spkey,spvalue in nested_dict['security_practices'].items():
            # For this security practice, is it a child of the current business function we're processing
            if bfvalue['id'] == spvalue['function']:
                practices.append(spvalue['name'])
                urls.append(name_to_slug(spvalue['name']))
        # Create a string for practices to go in the business function markdown header
        practices_markdown = ''
        for i,spname in enumerate(practices):
            spnum = i+1
            practices_markdown += 'practice_'+str(spnum)+': '+spname+'\npractice_'+str(spnum)+'_url: '+urls[i]+'\n'
        # Set output file name
        filename = args.output+'/'+name_to_slug(bfvalue['name'])+'.md'
        # Set variables for the business function template
        variables = {
            'name': bfvalue['name'],
            'slug': name_to_slug(bfvalue['name']),
            'description': bfvalue['description'],
            'practices': practices_markdown
        }
        # Create the Markdown file based on template and variables
        process_template('templates/business_function.md', filename, variables)

    '''
    WRITE SECURITY PRACTICE FILES
    '''

    # Make sure the output directory for practices exists, create it if not
    ensure_directory_exists(args.output+"/practice")
    # Loop through each security practice
    for spkey,spvalue in nested_dict['security_practices'].items():
        # Get details of the parent business function
        # Loop through the business functions
        # Set default values to not found in case we don't find it
        function_name = 'Function Not Found'
        function_slug = 'function_not_found'
        for bfkey,bfvalue in nested_dict['business_functions'].items():
            # If the current business function matches the ID we have in the security practice
            if spvalue['function'] == bfvalue['id']:
                function_name = bfvalue['name']
                function_slug = name_to_slug(bfvalue['name'])
        # Get the maturity level descriptions for the practice
        # Loop through each practice level and append to the list as we find matching levels
        practice_levels = []
        for plkey,plvalue in nested_dict['practice_levels'].items():
            # If the current practice level matches the ID we have in the security practice
            if plvalue['practice'] == spvalue['id']:
                practice_levels.append(plvalue['objective'])
        # Write a string to include maturity level descriptions in the markdown header
        practice_levels_markdown = ''
        for i,pldescription in enumerate(practice_levels):
            plnum = i+1
            practice_levels_markdown += 'practice_maturity_'+str(plnum)+'_description: '+pldescription+'\n'
        # Get the streams and activity descriptions for each maturity level
        # Loop throught streams to find those which belong to this practice
        streams_markdown = ''
        for stmkey,stmvalue in nested_dict['streams'].items():
            if stmvalue['practice'] == spvalue['id']:
                # Loop through activities to find those which belong to this stream
                activity_markdown = ''
                for actkey,actvalue in nested_dict['activities'].items():
                    if actvalue['stream'] == stmvalue['id']:
                        # Found relevant activitiy
                        # Set variables for the practice stream activity template
                        variables = {
                            'stream': stmvalue['letter'],
                            'maturity': levelid_to_level(nested_dict,actvalue['level']),
                            'description': actvalue['shortDescription']
                        }
                        activity_markdown += process_template_content('templates/security_practice_stream_activity.md',variables)+'\n'
                # Set variables for the practice stream template
                variables = {
                    'name': stmvalue['name'],
                    'letter': stmvalue['letter'],
                    'activities': activity_markdown
                }
                streams_markdown += process_template_content('templates/security_practice_stream.md',variables)+'\n'

        # Set output file name
        filename = args.output+'/practice/'+function_slug+'-'+name_to_slug(spvalue['shortName'])+'.md'
        # Set variables for the business function template
        variables = {
            'name': spvalue['name'],
            'slug': name_to_slug(spvalue['name']),
            'long_description': spvalue['longDescription'],
            'function_slug': function_slug,
            'function_name': function_name,
            'practice_levels': practice_levels_markdown,
            'streams': streams_markdown
        }
        # Create the Markdown file based on template and variables
        process_template('templates/security_practice.md', filename, variables)

    '''
    WRITE STREAM FILES
    '''

    # Make sure the output directory for practices exists, create it if not
    ensure_directory_exists(args.output+"/practice/stream")
    # Loop through each stream
    for stmkey,stmvalue in nested_dict['streams'].items():
        # Get details of the practice for this stream
        practice_name = 'Practice Not Found'
        practice_slug = 'practice_not_found'
        for spkey,spvalue in nested_dict['security_practices'].items():
            # If the current security pratice matches the ID we have in the stream
            if stmvalue['practice'] == spvalue['id']:
                practice_name = spvalue['name']
                practice_slug = name_to_slug(spvalue['name'])
                practice_short = spvalue['shortName']
                # Now get the function
                function_name = 'Function Not Found'
                function_slug = 'function_not_found'
                for bfkey,bfvalue in nested_dict['business_functions'].items():
                    # If the current business function matches the ID we have in the security practice
                    if spvalue['function'] == bfvalue['id']:
                        function_name = bfvalue['name']
                        function_slug = name_to_slug(bfvalue['name'])
        # Get content of each level of the stream
        level_markdown = ''
        # Loop through activities to find those which belong to this stream
        for actkey,actvalue in nested_dict['activities'].items():
            if actvalue['stream'] == stmvalue['id']:
                # Found relevant activitiy
                # Now get question and criteria details
                for qkey,qvalue in nested_dict['questions'].items():
                    if actvalue['id'] == qvalue['activity']:
                        question = qvalue['text']
                        answer_set_id = qvalue['answerset']
                        criteria = ''
                        for critvalue in qvalue['quality']:
                            criteria += '- '+critvalue+'\n'
                # Now get answer set
                answer_set_markdown = ''
                for asetkey,asetvalue in nested_dict['answer_sets'].items():
                    if asetvalue['id'] == answer_set_id:
                        for ansvalue in asetvalue['values']:
                            answer_set_markdown += '- '+fix_bool(ansvalue['text'])+'\n'

                # Set variables for the stream level template
                variables = {
                    'benefit': actvalue['benefit'],
                    'number': levelid_to_level(nested_dict,actvalue['level']),
                    'long_description': fix_indent(actvalue['longDescription'],3),
                    'question': question,
                    'criteria': fix_indent(criteria,3),
                    'answers': fix_indent(answer_set_markdown,3)
                }
                level_markdown += process_template_content('templates/stream_level.md',variables)+'\n'
        # Set variables for the stream template
        variables = {
            'name': stmvalue['name'],
            'function_slug': function_slug,
            'practice_slug': practice_slug,
            'letter': stmvalue['letter'],
            'function_name': function_name,
            'practice_name': practice_name,
            'levels': level_markdown
        }
         # Set output file name
        filename = args.output+'/practice/stream/'+function_slug+'-'+practice_short+'-'+stmvalue['letter']+'.md'
        # Create the Markdown file based on template and variables
        process_template('templates/stream.md', filename, variables)
