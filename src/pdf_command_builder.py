import os
import pprint
import pymupdf
import json
import re
import enum

from typing import Final, TypedDict

class CommandDetails(TypedDict):
    command_name: str
    query: str
    return_description: str
    is_implemented: bool
    parameters: dict | None = None

class ReturnElement(enum.Enum):
    NR1_FORMAT = "NR1"
    NR3_FORMAT = "NR3"
    UNQUOTED_STRING = "UNQUOTED"
    QUOTED_STRING = "QUOTED"
    ENUM_FORMAT = "ENUM"
    INLINE_ENUM_FORMAT = "INLINE_ENUM"
    UNKNOWN = "UNKNOWN"

file_path = os.path.join(os.getcwd(), '..', 'example.pdf')

doc = pymupdf.open('DSO5012A Programmers Guide.pdf')

COMMAND_TABLE_ROW: Final = ['Command', 'Query', 'Options and Query Returns']

# See page 106 of manual for a more in-depth explanation
OPTIONAL_SYNTAX: Final = ['[',']']
ENUM_BRACES: Final = ['{','}']
ANGLE_BRACKETS: Final = ['<','>'] # These can represent a string, or a command input

BRACKETED_SYNTAX: Final = OPTIONAL_SYNTAX + ENUM_BRACES + ANGLE_BRACKETS

# The above PDF, when read in, appears to have some formatting issues around the titles.

table_of_contents = doc.get_toc()
should_print_second_level = False

command_categories = []
command_list = []

for level, title, page in table_of_contents:
    # print(level, title, page)
    if level == 1:
        print(f'Top Level Page Contents are: {level, title, page}')
        # get the tables for the commands. We'll grab the titles from the table of contents,
        # and then compare them to the table titles
    elif should_print_second_level:
        print('Sub level page contents are: ', level, title, page)
        if level == 2:
            command_categories.append(title.replace(" Commands", ""))
        elif level == 3:
            command_list.append(title)
    if not should_print_second_level and 'subsystem' in title.lower():
        should_print_second_level = True
        continue
    # Stop printing the table of contents when we reach the end of the commands
    if should_print_second_level and level == 1:
        should_print_second_level = False

print(f'command_categories: {command_categories}')
# With the categories collected, we can now search for the tables we're interested in.

page_num = 0

scope_queries = { category : [] for category in command_categories }

scope_commands = { category : [] for category in command_categories }

detailed_commands_by_category = { category : [] for category in command_categories }

scope_options = {}

nr1_format_count = 0

scope_return_values_count = {}

single_range_pair = {}

def command_has_inline_range(formatted_command: str) -> bool:
    # Sometimes, the command will state the options it can accept, so use this function to check for that
    enum_braces = { bracket_character: 0 for bracket_character in ENUM_BRACES }
    for character in ENUM_BRACES:
        enum_braces[character] = formatted_command.count(character)
    for _, value in enum_braces.items():
        if value < 1:
            return False
    return True

def get_bracket_count(formatted_string: str) -> dict:
    return { bracket: formatted_string.count(bracket) for bracket in BRACKETED_SYNTAX }

# Note: There exists some text with misaligned brackets inside the PDF, so at some stage we will be required to
# account for that.
def has_no_named_variables(bracket_count: dict) -> bool:
    return bracket_count['<'] == 0 and bracket_count['>'] == 0
 
def has_single_named_variable(bracket_count: dict) -> bool:
    return bracket_count['<'] == 1 and bracket_count['>'] == 1

def has_enum_range_defined(bracket_count):
    return bracket_count['{'] >= 1 and bracket_count['}'] >= 1

def get_enum_values(formatted_command: str) -> list[str]:
    new_command = formatted_command
    # Flatten the nested enums - they are set values, and this allows for easier processing
    if formatted_command.count('}') > 1:
        new_command = formatted_command.replace(" ", "").replace("{0|OFF}", "OFF").replace("{1|ON}", "ON")
        # handle the one command that has the {{1|2}|{3|4}} format :)
        new_command = new_command.replace("{1|2}|{3|4}", "1|2|3|4")
    # "new_command" should deal with the nested brackets, so now the option can be placed in as a single
    string_to_get = re.findall(r'{(.*?)}', new_command)
    return string_to_get[0].split('|')

def determine_value_type(return_line_description: str) -> ReturnElement:
    line_to_target = return_line_description.lower()
    if 'nr1' in line_to_target:
        return ReturnElement.NR1_FORMAT
    elif 'nr3' in line_to_target:
        return ReturnElement.NR3_FORMAT
    elif 'unquoted' in line_to_target:
        return ReturnElement.UNQUOTED_STRING
    elif 'quoted' in line_to_target:
        return ReturnElement.QUOTED_STRING
    elif has_enum_range_defined(get_bracket_count(line_to_target)):
        return ReturnElement.ENUM_FORMAT
    else:
        return ReturnElement.UNKNOWN



def get_option_names(formatted_command: str) -> None:
    variable_stack = []
    should_begin_appending = False
    for character in formatted_command:
        if character == '<':
            should_begin_appending = True
            continue
        elif character == '>':
            should_begin_appending = False
            variable_name = ''.join(variable_stack)
            if variable_name in scope_options:
                scope_options[variable_name] += 1
            else:
                scope_options[variable_name] = 1    
        if should_begin_appending:
            variable_stack.append(character)
            



for page in doc:
    page_num += 1
    table_checker = page.find_tables()
    if len(table_checker.tables) != 0:
        # print(f'Page {page_num} has {len(table_checker.tables)} table(s)')
        # print(dir(table_checker.tables[0].header))
        focused_header = table_checker.tables[0].header
        for category in command_categories:
            try:
                joined_focused_header = ' '.join(focused_header.names)
            except TypeError:
                # there's probably a NoneType here, replace it with an empty string for now
                joined_focused_header = ' '.join([item if item is not None else '' for item in focused_header.names ])
            if category in joined_focused_header:
                # print(f'Table header is: {focused_header}')
                # print(f'Table headings are: {table_checker.tables[0].header.names}')
                # print(f'Table is: {table_checker.tables[0].extract()}')
                focused_table = table_checker.tables[0].extract()
                if focused_table[0] == COMMAND_TABLE_ROW:
                    print(f'IS COMMAND_TABLE')
                    print(f'Table is: {focused_table}')
                    # Format the commands and queries here
                    for command, query, return_description in focused_table[1:]:
                        detailed_command_dictionary = {}
                        has_variables_in_command = False
                        has_inline_variables_in_command = False
                        has_variables_in_query = False
                        has_inline_variables_in_query = False
                        detailed_command_params: dict[list] = {}
                        command_variable_names: list[str] = []
                        query_variable_names: list[str] = []
                        parameter_list: list[dict] = []
                        detailed_command_dictionary['parameters'] = parameter_list
                        # The text inside the PDF has awkward formatting, so it needs some cleaning up
                        if (formatted_command := command.split('(')[0].replace('\n', '').rstrip()) != 'n/a':
                            scope_commands[category].append(formatted_command)
                            print(f'Formatted command is: {formatted_command}')
                            # This deals with named commands
                            command_variable_names = re.findall(r'<(.*?)>', formatted_command)
                            has_variables_in_command = len(command_variable_names) > 0
                            # Some commands may contain a range of values. These are inline enums, not defined in the return items at all.
                            # We'll list them as inline enums
                            detailed_command_dictionary['command_name'] = formatted_command
                            bracket_count = get_bracket_count(formatted_command)
                            # inline command params dealt with here
                            if has_no_named_variables(bracket_count) and has_enum_range_defined(bracket_count):
                                inline_command_range = get_enum_values(formatted_command)
                                has_inline_variables_in_command = True
                                detailed_command_dictionary['parameters'].append({
                                    'INLINE_COMMAND_PARAMS': inline_command_range
                                })
                        if (formatted_query := query.split('(')[0].replace('\n', '').rstrip()) != 'n/a':
                            scope_queries[category].append(formatted_query)
                            query_variable_names = re.findall(r'<(.*?)>', formatted_query)
                            has_variables_in_query = len(query_variable_names) > 0
                            if any(bracket in formatted_query for bracket in BRACKETED_SYNTAX):
                                # enter the function to get option details
                                # query_parameter_details = get_parameter_details()
                                get_option_names(formatted_query)
                            detailed_command_dictionary['query'] = formatted_query
                            bracket_count = get_bracket_count(formatted_query)
                            if has_no_named_variables(bracket_count) and has_enum_range_defined(bracket_count):
                                inline_query_range = get_enum_values(formatted_query)
                                has_inline_variables_in_query = True
                                detailed_command_params['INLINE_QUERY_PARAMS'] = inline_query_range
                        formatted_return_description = return_description.replace('\n', '').rstrip()
                        if formatted_return_description in scope_return_values_count:
                            scope_return_values_count[formatted_return_description] += 1
                        else:
                            scope_return_values_count[formatted_return_description] = 1
                        if has_variables_in_command or has_variables_in_query:
                            # divide out the variables from the return description, and process them with the command ones
                            divided_out_variables = re.findall(r'<.*?>.*?(?=<|$)', formatted_return_description)
                            for section in divided_out_variables:
                                print(f'Section is: {section}')
                                [return_description_variable] = re.findall(r'<(.*?)>', section)
                                if return_description_variable == 'return_value':
                                    continue
                                print(f'Variable name capture is: {return_description_variable}')
                                value_type = determine_value_type(section)
                                if value_type == ReturnElement.ENUM_FORMAT:
                                    enum_variables = re.findall(r'{(.*?)}', formatted_return_description)
                                    formatted_variable_name_list = [item.strip(" ") for item in enum_variables[0].split('|')]
                                    print(f'Variable name set is: {formatted_variable_name_list}')
                                    detailed_command_dictionary['parameters'].append(
                                        {
                                            return_description_variable: formatted_variable_name_list
                                        }
                                    )
                                    detailed_command_dictionary['is_implemented'] = True
                                    continue
                                elif value_type == ReturnElement.UNKNOWN:
                                    print(f'Unknown return type: {section}')
                                    detailed_command_dictionary['is_implemented'] = False
                                    continue
                                detailed_command_dictionary['is_implemented'] = True
                                detailed_command_dictionary['parameters'].append({
                                    return_description_variable: value_type.value
                                })
                        detailed_command_dictionary['return_description'] = formatted_return_description
                        detailed_commands_by_category[category].append(detailed_command_dictionary)



                                

        # if 'Command' in focused_header.names:
        #     print(f'Table header is: {focused_header}')
        #     print(f'Table headings are: {table_checker.tables[0].header.names}')
        #     print(f'Table is: {table_checker.tables[0].rows[0].cells}')
print(f'Total number of pages: {page_num}')

print("Scope Queries")
pprint.pprint(scope_queries)

print("Scope Commands")
pprint.pprint(scope_commands)
# target_page = doc.load_page(109)

# print(target_page.get_text())

data = {
    'DSO5012A': {
        'Scope Queries': scope_queries,
        'Scope Commands': scope_commands,
        'Detailed Commands': detailed_commands_by_category
    }
}

with open('output.json', 'w') as f:
    json.dump(data, f, indent=4)

pprint.pprint(scope_options)

print(f'Number of scope options: {len(scope_options)}')

print(f'Number of NR1 format returns: {nr1_format_count}')

pprint.pprint(scope_return_values_count)

print(len(scope_return_values_count))