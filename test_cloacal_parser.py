from collections import OrderedDict

from cloacal_parser import format_clo_string, parse_clo


def test_parse_basic_input():
    clo_input = """
    +--------------+
    |   Carlisle   |
    +--------------+

    age ------- 99
    species --- seagull
    ilk ------- bird

    description -------------------------------
      Id ipsum elit tempor non incididunt laborum
      anim dolore eu fugiat. Dolor consectetur aute
      occaecat. Ex do reprehenderit nulla sunt dolor
      laborum qui. Qui voluptate tempor excepteur
      ex ea excepteur. Ipsum do elit fugiat laboris
      veniam pariatur.

    memories ----------------------------------
      >  Consectetur ut qui Lorem ad.
      >  Veniam mollit nostrud velit laborum laborum
         veniam irure ut aute magna labore aliqua.
      >  Magna reprehenderit anim esse aliquip magna
         do reprehenderit pariatur laborum do dolor.
    """

    expected_output = OrderedDict(
        {
            "name": "Carlisle",
            "age": "99",
            "species": "seagull",
            "ilk": "bird",
            "description": (
                "Id ipsum elit tempor non incididunt laborum anim dolore eu fugiat. Dolor consectetur aute "
                "occaecat. Ex do reprehenderit nulla sunt dolor laborum qui. Qui voluptate tempor excepteur "
                "ex ea excepteur. Ipsum do elit fugiat laboris veniam pariatur."
            ),
            "memories": [
                "Consectetur ut qui Lorem ad.",
                "Veniam mollit nostrud velit laborum laborum veniam irure ut aute magna labore aliqua.",
                "Magna reprehenderit anim esse aliquip magna do reprehenderit pariatur laborum do dolor.",
            ],
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_inconsistent_formatting():
    clo_input = """
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

    expected_output = OrderedDict(
        {
            "name": "Carlisle",
            "age": "99",
            "species": "seagull",
            "ilk": "bird",
            "description": (
                "Id ipsum elit tempor non incididunt laborum anim dolore eu fugiat. Dolor consectetur aute "
                "occaecat. Ex do reprehenderit nulla sunt dolor laborum qui. Qui voluptate tempor excepteur "
                "ex ea excepteur. Ipsum do elit fugiat laboris veniam pariatur."
            ),
            "memories": [
                "Consectetur ut qui Lorem ad.",
                "Veniam mollit nostrud velit laborum laborum veniam irure ut aute magna labore aliqua.",
                "Magna reprehenderit anim esse aliquip magna do reprehenderit pariatur laborum do dolor.",
            ],
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_missing_fields():
    clo_input = """
    +--+
    | Anonymous |
    +-----

    species - unknown

    description ----
      This character has no age or ilk specified.
    """

    expected_output = OrderedDict(
        {
            "name": "Anonymous",
            "species": "unknown",
            "description": "This character has no age or ilk specified.",
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_empty_input():
    clo_input = ""

    expected_output = OrderedDict({})

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_no_name_box():
    clo_input = """
    age ------- 25
    species --- human
    ilk ------- warrior

    description -------------------------------
      A brave warrior with no name box.
    """

    expected_output = OrderedDict(
        {
            "age": "25",
            "species": "human",
            "ilk": "warrior",
            "description": "A brave warrior with no name box.",
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_multiple_blocks():
    clo_input = """
    +--+
    | MultiBlock |
    +-----

    abilities ----------------------
      Strength, Agility, Intelligence

    inventory ----------------------
      > Sword
      > Shield
      > Potion

    notes --------------------------
      This character has multiple block sections.
    """

    expected_output = OrderedDict(
        {
            "name": "MultiBlock",
            "abilities": "Strength, Agility, Intelligence",
            "inventory": ["Sword", "Shield", "Potion"],
            "notes": "This character has multiple block sections.",
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_unexpected_formatting():
    clo_input = """
    +--+
    | Mysterious |
    +-----

    age: unknown
    species == alien

    description ~~~
      Lines with unusual formatting should be ignored or parsed correctly.

    memories >>>
      > First encounter.
      > Strange symbols.

    extra_data ----------------------------------
      This block should be parsed even with unusual header formatting.
    """

    expected_output = OrderedDict(
        {
            "name": "Mysterious",
            "description": "Lines with unusual formatting should be ignored or parsed correctly.",
            "memories": ["First encounter.", "Strange symbols."],
            "extra_data": "This block should be parsed even with unusual header formatting.",
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_nested_lists():
    clo_input = """
    +--+
    | NestedList |
    +-----

    tasks ----------------------------------
      > Task 1
        > Subtask 1.1
        > Subtask 1.2
      > Task 2

    description ----------------------------
      Testing nested lists (should be flattened).
    """

    expected_output = OrderedDict(
        {
            "name": "NestedList",
            "tasks": ["Task 1 Subtask 1.1 Subtask 1.2", "Task 2"],
            "description": "Testing nested lists (should be flattened).",
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_parse_block_without_content():
    clo_input = """
    +--+
    | EmptyBlock |
    +-----

    description ----

    memories ----

    age --- 30
    """

    expected_output = OrderedDict(
        {
            "name": "EmptyBlock",
            "age": "30",
            # description and memories are empty, so they may be absent or present with empty values
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output or result == {
        "name": "EmptyBlock",
        "description": "",
        "memories": "",
        "age": "30",
    }


def test_parse_incorrect_indentation():
    clo_input = """
    +--+
    | IndentationTest |
    +-----

    description -------------------------------
    Id ipsum elit tempor non incididunt laborum
    anim dolore eu fugiat.

    memories ----------------------------------
    > Consectetur ut qui Lorem ad.
    >Veniam mollit nostrud velit laborum laborum
    veniam irure ut aute magna labore aliqua.
    >  Magna reprehenderit anim esse aliquip magna
    do reprehenderit pariatur laborum do dolor.
    """

    expected_output = OrderedDict(
        {
            "name": "IndentationTest",
            "description": "Id ipsum elit tempor non incididunt laborum anim dolore eu fugiat.",
            "memories": [
                "Consectetur ut qui Lorem ad.",
                "Veniam mollit nostrud velit laborum laborum veniam irure ut aute magna labore aliqua.",
                "Magna reprehenderit anim esse aliquip magna do reprehenderit pariatur laborum do dolor.",
            ],
        }
    )

    result = parse_clo(clo_input)
    assert result == expected_output


def test_format_basic_input():
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

    expected_output = """
+------------------------------------------+
|                 Carlisle                  |
+------------------------------------------+

age ------- 99
ilk ------- bird
species --- seagull

description -------------------------------
  Id ipsum elit tempor non incididunt
  laborum anim dolore eu fugiat. Dolor
  consectetur aute occaecat. Ex do
  reprehenderit nulla sunt dolor laborum
  qui. Qui voluptate tempor excepteur ex ea
  excepteur. Ipsum do elit fugiat laboris
  veniam pariatur.

memories ----------------------------------
  > Consectetur ut qui Lorem ad.
  > Veniam mollit nostrud velit laborum
    laborum veniam irure ut aute magna
    labore aliqua.
  > Magna reprehenderit anim esse aliquip
    magna do reprehenderit pariatur laborum
    do dolor.
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_missing_name():
    ugly_input = """
    age -- 30
    species - human

    description ----
         A character with no name box.
    """

    expected_output = """
age ------- 30
species --- human

description -------------------------------
  A character with no name box.
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_empty_input():
    ugly_input = ""

    expected_output = ""

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_only_name():
    ugly_input = """
    +--+
    | Solo |
    +-----
    """

    expected_output = """
+------------------------------------------+
|                   Solo                    |
+------------------------------------------+
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_unexpected_content():
    ugly_input = """
    +--+
    | Random |
    +-----

    age -- 22
    unknown_field **** data

    description ----
         Contains unexpected content.
    """

    expected_output = """
+--------+
| Random |
+--------+

age ------------- 22
description ----- Contains unexpected content.
unknown_field --- data
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_long_name():
    ugly_input = """
    +--+
    | The Great and Powerful Name |
    +-----

    age -- 100
    species - mythical creature
    """

    expected_output = """
+------------------------------------------+
|        The Great and Powerful Name        |
+------------------------------------------+

age ------- 100
species --- mythical creature
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_block_without_content():
    ugly_input = """
    +--+
    | EmptyBlock |
    +-----

    age --- 30

    description ----

    memories ----
    """

    expected_output = """
+------------------------------------------+
|                EmptyBlock                 |
+------------------------------------------+

age ----------- 30
description ---
memories ------
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output


def test_format_multiple_blocks():
    ugly_input = """
    +--+
    | MultiBlock |
    +-----

    abilities ----------------------
      Strength, Agility, Intelligence

    inventory ----------------------
      > Sword
      > Shield
      > Potion

    notes --------------------------
      This character has multiple block sections.
    """

    expected_output = """
+------------------------------------------+
|                MultiBlock                 |
+------------------------------------------+

abilities --- Strength, Agility, Intelligence

inventory ---------------------------------
  > Sword
  > Shield
  > Potion

notes -------------------------------------
  This character has multiple block
  sections.
""".strip()

    formatted_output = format_clo_string(ugly_input)
    assert formatted_output == expected_output
