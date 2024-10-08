import pprint
import pymupdf
import json
import re
import enum
import argparse
import os

from dataclasses import dataclass, field, asdict
from typing import Final
from dotenv import load_dotenv

# See page 106 of manual for a more in-depth explanation
OPTIONAL_SYNTAX: Final = ["[", "]"]
ENUM_BRACES: Final = ["{", "}"]
ANGLE_BRACKETS: Final = ["<", ">"]  # These can represent a string, or a command input

BRACKETED_SYNTAX: Final = OPTIONAL_SYNTAX + ENUM_BRACES + ANGLE_BRACKETS


class ReturnElement(enum.Enum):
    NR1_FORMAT = "NR1"
    NR3_FORMAT = "NR3"
    UNQUOTED_STRING = "UNQUOTED"
    QUOTED_STRING = "QUOTED"
    ENUM_FORMAT = "ENUM"
    INLINE_ENUM_FORMAT = "INLINE_ENUM"
    UNKNOWN = "UNKNOWN"


@dataclass
class CommandDetails:
    has_variables_in_command: bool = False
    has_inline_variables_in_command: bool = False
    has_variables_in_query: bool = False
    has_inline_variables_in_query: bool = False
    command_variable_names: list[str] = field(default_factory=list)
    query_variable_names: list[str] = field(default_factory=list)
    variable_list: list[dict] = field(default_factory=list)
    command_name: str | None = None
    query_name: str | None = None
    return_description: str | None = None
    is_implemented: bool = False


def parse_command_line_args(env_filepath: str = ".env"):
    load_dotenv(env_filepath)
    parser = argparse.ArgumentParser(
        description="Extracts command information from a PDF file, and enters it into a JSON file."
    )
    parser.add_argument(
        "--pdf-file-path",
        type=str,
        help="The PDF file to extract command information from.",
        default=os.environ["PDF_FILE_PATH"],
    )
    parser.add_argument(
        "--output-file-path",
        type=str,
        help="The JSON file to output the command information to.",
        default=os.environ["OUTPUT_FILE_PATH"],
    )
    return parser.parse_args()


def obtain_commands_to_process(
    doc: pymupdf.Document, command_categories: list[str], command_list: list[str]
):
    table_of_contents = doc.get_toc()
    is_obtaining_command_details = False
    print("Processing Table of Contents...")
    for level, title, _ in table_of_contents:
        if (
            not is_obtaining_command_details
            and "commands by subsystem" in title.lower()
        ):
            print("Command details found: Starting to process...")
            is_obtaining_command_details = True
            continue
        elif is_obtaining_command_details:
            if level == 1:
                is_obtaining_command_details = False
            elif level == 2:
                command_category = title.replace(" Commands", "")
                print(f"Adding {command_category} to command_categories...")
                command_categories.append(title.replace(" Commands", ""))
            elif level == 3:
                print(f"Adding {title} to command_list...")
                command_list.append(title)


def command_has_inline_range(formatted_command: str) -> bool:
    # Sometimes, the command will state the options it can accept, so use this function to check for that
    enum_braces = {bracket_character: 0 for bracket_character in ENUM_BRACES}
    for character in ENUM_BRACES:
        enum_braces[character] = formatted_command.count(character)
    for _, value in enum_braces.items():
        if value < 1:
            return False
    return True


def get_bracket_count(formatted_string: str) -> dict:
    return {bracket: formatted_string.count(bracket) for bracket in BRACKETED_SYNTAX}


# Note: There exists some text with misaligned brackets inside the PDF, so at some stage we will be required to
# account for that.
def has_no_named_variables(bracket_count: dict) -> bool:
    return bracket_count["<"] == 0 and bracket_count[">"] == 0


def has_single_named_variable(bracket_count: dict) -> bool:
    return bracket_count["<"] == 1 and bracket_count[">"] == 1


def has_enum_range_defined(bracket_count):
    return bracket_count["{"] >= 1 and bracket_count["}"] >= 1


def get_enum_values(formatted_command: str) -> list[str]:
    new_command = formatted_command
    # Flatten the nested enums - they are set values, and this allows for easier processing
    if formatted_command.count("}") > 1:
        new_command = (
            formatted_command.replace(" ", "")
            .replace("{0|OFF}", "OFF")
            .replace("{1|ON}", "ON")
        )
        # handle the one command that has the {{1|2}|{3|4}} format :)
        new_command = new_command.replace("{1|2}|{3|4}", "1|2|3|4")
    # "new_command" should deal with the nested brackets, so now the option can be placed in as a single
    string_to_get = re.findall(r"{(.*?)}", new_command)
    return string_to_get[0].split("|")


def determine_value_type(return_line_description: str) -> ReturnElement:
    line_to_target = return_line_description.lower()
    if "nr1" in line_to_target:
        return ReturnElement.NR1_FORMAT
    elif "nr3" in line_to_target:
        return ReturnElement.NR3_FORMAT
    elif "unquoted" in line_to_target:
        return ReturnElement.UNQUOTED_STRING
    elif "quoted" in line_to_target:
        return ReturnElement.QUOTED_STRING
    elif has_enum_range_defined(get_bracket_count(line_to_target)):
        return ReturnElement.ENUM_FORMAT
    else:
        return ReturnElement.UNKNOWN


def prcoess_command_details(
    detailed_commands_by_category: dict[str, dict],
    scope_queries: dict,
    scope_commands: dict,
    doc: pymupdf.Document,
    command_categories: list[str],
) -> None:
    COMMAND_TABLE_ROW: Final = ["Command", "Query", "Options and Query Returns"]
    for page in doc:
        table_checker = page.find_tables()
        if len(table_checker.tables) != 0:
            focused_header = table_checker.tables[0].header
            for category in command_categories:
                try:
                    joined_focused_header = " ".join(focused_header.names)
                except TypeError:
                    # there's probably a NoneType here, replace it with an empty string for now
                    joined_focused_header = " ".join(
                        [
                            item if item is not None else ""
                            for item in focused_header.names
                        ]
                    )
                if category in joined_focused_header:
                    # print(f'Table header is: {focused_header}')
                    # print(f'Table headings are: {table_checker.tables[0].header.names}')
                    # print(f'Table is: {table_checker.tables[0].extract()}')
                    focused_table = table_checker.tables[0].extract()
                    if focused_table[0] == COMMAND_TABLE_ROW:
                        print(f"IS COMMAND_TABLE")
                        print(f"Table is: {focused_table}")
                        for command, query, return_description in focused_table[1:]:
                            command_details = CommandDetails()
                            # The text inside the PDF has awkward formatting, so it needs some cleaning up
                            if (
                                formatted_command := command.split("(")[0]
                                .replace("\n", "")
                                .rstrip()
                            ) != "n/a":
                                scope_commands[category].append(formatted_command)
                                print(f"Formatted command is: {formatted_command}")
                                # This deals with named commands
                                command_details.command_name = formatted_command
                                command_details.command_variable_names = re.findall(
                                    r"<(.*?)>", formatted_command
                                )
                                command_details.has_variables_in_command = (
                                    len(command_details.command_variable_names) > 0
                                )
                                bracket_count = get_bracket_count(formatted_command)
                                # inline command params dealt with here
                                if has_no_named_variables(
                                    bracket_count
                                ) and has_enum_range_defined(bracket_count):
                                    inline_command_range = get_enum_values(
                                        formatted_command
                                    )
                                    command_details.has_inline_variables_in_command = (
                                        True
                                    )
                                    command_details.variable_list.append(
                                        {"INLINE_COMMAND_PARAMS": inline_command_range}
                                    )
                            if (
                                formatted_query := query.split("(")[0]
                                .replace("\n", "")
                                .rstrip()
                            ) != "n/a":
                                scope_queries[category].append(formatted_query)
                                print(f"Formatted query is: {formatted_query}")
                                # deals with named queries
                                command_details.query_name = formatted_query
                                command_details.query_variable_names = re.findall(
                                    r"<(.*?)>", formatted_query
                                )
                                command_details.has_variables_in_query = (
                                    len(command_details.query_variable_names) > 0
                                )
                                bracket_count = get_bracket_count(formatted_query)
                                # inline query params dealt with here
                                if has_no_named_variables(
                                    bracket_count
                                ) and has_enum_range_defined(bracket_count):
                                    inline_query_range = get_enum_values(
                                        formatted_query
                                    )
                                    command_details.has_inline_variables_in_query = True
                                    command_details.variable_list.append(
                                        ({"INLINE_QUERY_PARAMS": inline_query_range})
                                    )
                            formatted_return_description = return_description.replace(
                                "\n", ""
                            ).rstrip()
                            command_details.return_description = (
                                formatted_return_description
                            )
                            if (
                                command_details.has_variables_in_command
                                or command_details.has_inline_variables_in_command
                            ):
                                # divide out the variables from the return description, and process them with the command ones
                                divided_out_variables = re.findall(
                                    r"<.*?>.*?(?=<|$)", formatted_return_description
                                )
                                contains_unprocessed_parameter = False
                                for section in divided_out_variables:
                                    print(f"Section is: {section}")
                                    [return_description_variable] = re.findall(
                                        r"<(.*?)>", section
                                    )
                                    if return_description_variable == "return_value":
                                        continue
                                    print(
                                        f"Variable name capture is: {return_description_variable}"
                                    )
                                    value_type = determine_value_type(section)
                                    if value_type == ReturnElement.ENUM_FORMAT:
                                        enum_variables = re.findall(
                                            r"{(.*?)}", formatted_return_description
                                        )
                                        formatted_variable_name_list = [
                                            item.strip(" ")
                                            for item in enum_variables[0].split("|")
                                        ]
                                        print(
                                            f"Variable name set is: {formatted_variable_name_list}"
                                        )
                                        command_details.variable_list.append(
                                            {
                                                return_description_variable: formatted_variable_name_list
                                            }
                                        )
                                        continue
                                    elif value_type == ReturnElement.UNKNOWN:
                                        print(f"Unknown return type: {section}")
                                        contains_unprocessed_parameter = True
                                        continue
                                    command_details.variable_list.append(
                                        {return_description_variable: value_type.value}
                                    )
                                command_details.is_implemented = (
                                    not contains_unprocessed_parameter
                                )
                            else:
                                command_details.is_implemented = True
                            detailed_commands_by_category[category].append(
                                asdict(command_details)
                            )


def write_command_data_to_file(
    output_file_path: str,
    scope_queries: dict,
    scope_commands: dict,
    detailed_commands_by_category: dict[str, dict],
):
    print(f"Writing command data to {output_file_path}...")
    data_to_write = {
        "DSO5012A": {
            "Scope Queries": scope_queries,
            "Scope Commands": scope_commands,
            "Detailed Commands": detailed_commands_by_category,
        }
    }
    print(f"Writing command data to {output_file_path}...")
    with open(os.path.join(output_file_path), "w", encoding="utf8") as f:
        try:
            json.dump(data_to_write, f, indent=4)
            print("Successfully wrote to file without errors!")
        except Exception as e:
            print(f"Error writing to file: {e}")


if __name__ == "__main__":
    args = parse_command_line_args()
    try:
        doc = pymupdf.open(args.pdf_file_path)
    except FileNotFoundError:
        print(
            f"The PDF file {args.pdf_file_path} could not be found. Check the path and try again."
        )
        exit(1)
    command_categories: list[str] = []
    command_list: list[str] = []
    obtain_commands_to_process(doc, command_categories, command_list)
    scope_queries = {category: [] for category in command_categories}
    scope_commands = {category: [] for category in command_categories}
    detailed_commands_by_category: dict[str, CommandDetails] = {
        category: [] for category in command_categories
    }
    prcoess_command_details(
        detailed_commands_by_category,
        scope_queries,
        scope_commands,
        doc,
        command_categories,
    )
    write_command_data_to_file(
        args.output_file_path,
        scope_queries,
        scope_commands,
        detailed_commands_by_category,
    )
    print("Scope Queries")
    pprint.pprint(scope_queries)
    print("Scope Commands")
    pprint.pprint(scope_commands)
