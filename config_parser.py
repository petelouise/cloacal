import re
import textwrap
from collections import OrderedDict


def parse_dsl(input_text):
    """
    Parses the DSL input text and returns an OrderedDict representing the data.
    """
    import re
    from collections import OrderedDict

    lines = input_text.strip("\n").split("\n")
    data = OrderedDict()
    i = 0
    n = len(lines)

    # Patterns to match block headers and key-value pairs
    block_header_pattern = re.compile(r"^\s*(\w+)\s*[-~>*]+\s*$")
    key_value_pattern = re.compile(
        r"^\s*(\w+)\s*[-~>*]+\s*(.+)$"
    )  # Accept various separators

    while i < n:
        line = lines[i]
        stripped_line = line.strip()

        # Skip empty lines
        if not stripped_line:
            i += 1
            continue

        # Check for name box
        if stripped_line.startswith("+"):
            # Name box detected
            if i + 1 < n and lines[i + 1].strip().startswith("|"):
                name_line = lines[i + 1].strip()
                name = name_line.strip("|").strip()
                data["name"] = name
                i += 3  # Skip the name box lines (+, | name |, +)
                continue
            else:
                i += 1
                continue

        # Check for block header (e.g., description ----)
        m = block_header_pattern.match(line)
        if m:
            key = m.group(1)
            i += 1
            block_lines = []
            list_items = []
            while i < n:
                block_line = lines[i]
                stripped_block_line = block_line.strip()

                if not stripped_block_line:
                    i += 1
                    continue

                # Check if this line is a new block header or key-value pair
                new_block_match = block_header_pattern.match(block_line)
                new_kv_match = key_value_pattern.match(block_line)
                if new_block_match or new_kv_match:
                    break  # New block or key-value pair detected

                if stripped_block_line.startswith(">"):
                    # Start of a new list item
                    current_item_lines = []
                    subtask_lines = []
                    # Get the first line of the item
                    item_line = stripped_block_line.lstrip(">").strip()
                    current_item_lines.append(item_line)
                    i += 1

                    # Collect continuation lines and subtasks for this item
                    while i < n:
                        next_line = lines[i].rstrip()
                        if not next_line.strip():
                            i += 1
                            continue

                        # Check if this is a new top-level list item or block
                        if (
                            (
                                next_line.strip().startswith(">")
                                and not next_line.startswith("        >")
                            )
                            or block_header_pattern.match(next_line)
                            or key_value_pattern.match(next_line)
                        ):
                            break

                        # If it's a subtask (more indented '>')
                        if next_line.strip().startswith(">") and next_line.startswith(
                            "        "
                        ):
                            subtask_lines.append(next_line.strip().lstrip(">").strip())
                            i += 1
                        # If it's an indented continuation line
                        elif next_line.startswith(" ") or next_line.startswith("\t"):
                            current_item_lines.append(next_line.strip())
                            i += 1
                        else:
                            break

                    # Join all lines for this item and its subtasks
                    item_text = " ".join(current_item_lines + subtask_lines)
                    list_items.append(item_text)
                elif block_line.startswith(" ") or block_line.startswith("\t"):
                    # Part of block text
                    block_lines.append(stripped_block_line)
                    i += 1
                else:
                    i += 1  # Skip unrecognized lines within a block
            # Check if this is a list block by looking for any '>' markers
            is_list_block = any(
                line.strip().startswith(">") for line in lines[i - 10 : i]
            )

            if list_items:
                data[key] = list_items
            elif block_lines:
                block_text = " ".join(block_lines)
                data[key] = block_text
            elif is_list_block:
                data[key] = []  # Empty list block
            else:
                data[key] = ""  # Empty text block
            continue

        # Check for key-value pair with value (e.g., age -- 99)
        m = key_value_pattern.match(line)
        if m:
            key = m.group(1)
            value = m.group(2).strip()
            data[key] = value
            i += 1
            continue

        # Unrecognized line, skip it
        i += 1

    return data


def format_dsl(data, max_line_length=44):
    """
    Formats the data OrderedDict into a nicely formatted DSL string.

    Args:
        data: OrderedDict containing the parsed DSL data
        max_line_length: Maximum length for wrapped lines (default: 44)
    """
    # Formatting parameters
    key_width = max((len(key) for key in data.keys() if key != "name"), default=0)
    dash_width = max(3, key_width)
    wrap_width = max_line_length
    indent = 2  # Indentation for block texts

    lines = []

    # Format the name box
    if "name" in data:
        name = data["name"]
        name_length = len(name)
        box_width = max(name_length + 4, 10)  # Minimum width to fit the name
        # Ensure box_width is even for perfect centering
        if box_width % 2 != 0:
            box_width += 1
        top_bottom = "+" + "-" * (box_width - 2) + "+"
        # Center the name with equal spaces on both sides
        name_padding = (box_width - 4 - len(name)) // 2
        middle = "| " + " " * name_padding + name + " " * name_padding + " |"
        # Adjust if name length causes uneven spacing
        if (box_width - 4 - len(name)) % 2 != 0:
            middle = middle[:-2] + "  |"
        lines.append(top_bottom)
        lines.append(middle)
        lines.append(top_bottom)
        lines.append("")  # Blank line

    # Sort simple key-value pairs
    simple_pairs = [
        (k, v)
        for k, v in data.items()
        if k != "name" and isinstance(v, str) and "\n" not in v and len(v.split()) <= 5
    ]
    sorted_pairs = sorted(simple_pairs)

    # Find the longest value to align all values
    max_value_pos = max(
        (len(key) + 3 for key, value in sorted_pairs),  # +3 for minimum dashes
        default=0,
    )

    # Process simple key-value pairs first
    for key, value in sorted_pairs:
        # Calculate dashes needed to align the value at max_value_pos
        dash_count = max_value_pos - len(key)
        dashes = "-" * dash_count
        line = f"{key} {dashes} {value}"
        lines.append(line)

    if simple_pairs:  # Add blank line after key-value pairs if any exist
        lines.append("")

    # Process remaining blocks in original order
    for key, value in data.items():
        if key == "name" or (key, value) in simple_pairs:
            continue

        if isinstance(value, list):
            # List block
            # Fill remaining space with dashes to reach max_line_length
            dash_count = (
                max_line_length - len(key) - 2
            )  # -2 for the space after key and end
            header_dashes = "-" * dash_count
            header_line = f"{key} {header_dashes}"
            lines.append(header_line)
            for item in value:
                # Calculate effective width for wrapping
                effective_width = wrap_width - indent - 2
                # Use break_long_words=False to prevent word splitting
                wrapped_item = textwrap.fill(
                    item,
                    width=effective_width,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                item_lines = wrapped_item.split("\n")
                indented_item = [" " * indent + "> " + item_lines[0]]
                indented_item += [" " * (indent + 2) + line for line in item_lines[1:]]
                lines.extend(indented_item)
            lines.append("")  # Blank line after each block
        else:
            # Block text
            # Fill remaining space with dashes to reach max_line_length
            dash_count = (
                max_line_length - len(key) - 2
            )  # -2 for the space after key and end
            header_dashes = "-" * dash_count
            header_line = f"{key} {header_dashes}"
            lines.append(header_line)
            # Calculate effective width for wrapping
            effective_width = wrap_width - indent
            # Use break_long_words=False to prevent word splitting
            wrapped_text = textwrap.fill(
                value,
                width=effective_width,
                break_long_words=False,
                break_on_hyphens=False,
            )
            indented_lines = [" " * indent + line for line in wrapped_text.split("\n")]
            lines.extend(indented_lines)
            lines.append("")  # Blank line after each block

    # Remove any trailing spaces from each line and join with newlines
    formatted_text = "\n".join(line.rstrip() for line in lines)
    # Ensure single trailing newline
    return formatted_text.strip("\n")


def format_dsl_string(input_text, max_line_length=44):
    """
    Takes an ugly DSL input string and returns a nicely formatted DSL string.

    Args:
        input_text: The input DSL string to format
        max_line_length: Maximum length for wrapped lines (default: 44)
    """
    data = parse_dsl(input_text)
    formatted_output = format_dsl(data, max_line_length=max_line_length)
    return formatted_output


if __name__ == "__main__":
    ugly_input = """
    +--+
    | Carlisle |
    +-----

    age -- 99
    species - seagull
    ilk ------------ bird

    description ----
         Id ipsum elit tempor non incididunt laborum
      anim dolore eu fugiat. Dolor consectetur aute occaecat. Ex do reprehenderit nulla sunt dolor
      laborum qui. Qui voluptate tempor excepteur
      ex ea excepteur. Ipsum do elit fugiat laboris
      veniam pariatur.

    memories -----------------------
      >    Consectetur ut qui Lorem ad.
      >  Veniam mollit nostrud velit laborum laborum veniam irure ut aute magna labore aliqua.
      > 	 Magna reprehenderit anim esse aliquip magna do reprehenderit pariatur laborum do dolor.
    """

    # Format the input string
    data = parse_dsl(ugly_input)
    print(data)
    formatted_output = format_dsl(data)
    print(formatted_output)
