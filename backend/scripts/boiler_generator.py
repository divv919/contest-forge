
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROBLEM_STATEMENTS_DIR = ROOT / "problem-statements"
ENV_KEYS = ("PROBLEM_SLUG", "problem_slug", "PROBLEM_ID", "problem_id", "SLUG", "slug")


def get_problem_slug() -> str:
    for key in ENV_KEYS:
        value = os.environ.get(key)
        if value:
            return value.strip()
    raise SystemExit(
        "Missing problem slug. Set one of: PROBLEM_SLUG, problem_slug, PROBLEM_ID, problem_id, SLUG, slug."
    )


def load_schema(problem_slug: str) -> dict[str, Any]:
    schema_path = PROBLEM_STATEMENTS_DIR / problem_slug / "problem-schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Problem schema not found: {schema_path}")
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_type(raw_type: str) -> tuple[str, str | None]:
    normalized = raw_type.strip().lower()
    if normalized.endswith("[]"):
        return "array", normalized[:-2].strip()
    if normalized.startswith("array<") and normalized.endswith(">"):
        return "array", normalized[6:-1].strip()
    if normalized.startswith("list<") and normalized.endswith(">"):
        return "array", normalized[5:-1].strip()
    return normalized, None


def cpp_type(raw_type: str) -> str:
    kind, inner = normalize_type(raw_type)
    if kind == "int":
        return "int"
    if kind == "bool":
        return "bool"
    if kind == "array":
        if inner == "int":
            return "vector<int>"
        if inner == "bool":
            return "vector<bool>"
        return "vector<string>"
    return "string"


def js_bool_parser() -> str:
    return """
function parseBool(value) {
    const normalized = String(value).trim().toLowerCase();
    return normalized === 'true' || normalized === '1';
}
""".strip()


def python_bool_parser() -> str:
    return """
def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"true", "1"}
""".strip()


def cpp_helpers() -> str:
    return """
#include <bits/stdc++.h>
using namespace std;

bool parseBool(const string& value) {
    string normalized = value;
    for (char& ch : normalized) {
        ch = static_cast<char>(tolower(static_cast<unsigned char>(ch)));
    }
    return normalized == "true" || normalized == "1";
}

string boolToString(bool value) {
    return value ? "true" : "false";
}
""".strip()


def js_full_boilerplate(schema: dict[str, Any]) -> str:
    inputs = list(schema["input_schema"].items())
    function_name = schema["result"]["function"]
    result_type = schema["result"]["type"].strip().lower()

    parser_lines: list[str] = []
    call_args: list[str] = []

    for name, raw_type in inputs:
        kind, inner = normalize_type(raw_type)
        if kind == "array":
            item_type = inner or "string"
            length_var = f"{name}Length"
            values_var = f"{name}Values"
            parser_lines.append(f"const {length_var} = Number(lines[index++]);")
            parser_lines.append(
                f"const {values_var} = (lines[index++] || '').trim().split(/\\s+/).filter(Boolean);"
            )
            if item_type == "int":
                parser_lines.append(
                    f"const {name} = {values_var}.slice(0, {length_var}).map((value) => Number(value));"
                )
            elif item_type == "bool":
                parser_lines.append(
                    f"const {name} = {values_var}.slice(0, {length_var}).map((value) => parseBool(value));"
                )
            else:
                parser_lines.append(f"const {name} = {values_var}.slice(0, {length_var});")
        else:
            if kind == "int":
                parser_lines.append(f"const {name} = Number(lines[index++]);")
            elif kind == "bool":
                parser_lines.append(f"const {name} = parseBool(lines[index++]);")
            else:
                parser_lines.append(f"const {name} = lines[index++];")
        call_args.append(name)

    result_serializer = {
        "int": "String(result)",
        "bool": "result ? 'true' : 'false'",
        "str": "result",
    }.get(result_type, "String(result)")

    parser_block = "\n".join(f"    {line}" for line in parser_lines)

    return f"""{js_bool_parser()}

<USER_CODE>

const fs = require('fs');

const rawInput = fs.readFileSync(0, 'utf8').replace(/\\r\\n/g, '\\n').trim();
const lines = rawInput.length === 0 ? [] : rawInput.split('\\n');
let index = 0;

{parser_block}

const result = {function_name}({', '.join(call_args)});
console.log({result_serializer});
""".strip() + "\n"


def js_user_boilerplate(schema: dict[str, Any]) -> str:
    inputs = list(schema["input_schema"].items())
    function_name = schema["result"]["function"]
    args = ", ".join(name for name, _ in inputs)
    return f"""function {function_name}({args}) {{
    // Write your code here
}}
"""


def python_full_boilerplate(schema: dict[str, Any]) -> str:
    inputs = list(schema["input_schema"].items())
    function_name = schema["result"]["function"]
    result_type = schema["result"]["type"].strip().lower()

    parser_lines: list[str] = []
    call_args: list[str] = []

    for name, raw_type in inputs:
        kind, inner = normalize_type(raw_type)
        if kind == "array":
            length_var = f"{name}_length"
            values_var = f"{name}_values"
            parser_lines.append(f"{length_var} = int(lines[index])")
            parser_lines.append("index += 1")
            parser_lines.append(f"{values_var} = lines[index].split() if index < len(lines) else []")
            parser_lines.append("index += 1")
            if inner == "int":
                parser_lines.append(f"{name} = [int(value) for value in {values_var}[:{length_var}]]")
            elif inner == "bool":
                parser_lines.append(f"{name} = [parse_bool(value) for value in {values_var}[:{length_var}]]")
            else:
                parser_lines.append(f"{name} = {values_var}[:{length_var}]")
        else:
            if kind == "int":
                parser_lines.append(f"{name} = int(lines[index])")
            elif kind == "bool":
                parser_lines.append(f"{name} = parse_bool(lines[index])")
            else:
                parser_lines.append(f"{name} = lines[index]")
            parser_lines.append("index += 1")
        call_args.append(name)

    result_serializer = {
        "int": "str(result)",
        "bool": "'true' if result else 'false'",
        "str": "result",
    }.get(result_type, "str(result)")

    parser_block = "\n".join(f"    {line}" for line in parser_lines)
    args = ", ".join(name for name, _ in inputs)

    return f"""{python_bool_parser()}

<USER_CODE>

def main() -> None:
    import sys

    raw_input = sys.stdin.read().rstrip("\\n")
    lines = raw_input.splitlines() if raw_input else []
    index = 0

{parser_block}

    result = {function_name}({', '.join(call_args)})
    print({result_serializer})


if __name__ == "__main__":
    main()
"""


def python_user_boilerplate(schema: dict[str, Any]) -> str:
    inputs = list(schema["input_schema"].items())
    function_name = schema["result"]["function"]
    args = ", ".join(name for name, _ in inputs)
    return f"""def {function_name}({args}):
    # Write your code here
    pass
"""


def cpp_full_boilerplate(schema: dict[str, Any]) -> str:
    inputs = list(schema["input_schema"].items())
    function_name = schema["result"]["function"]
    result_type = schema["result"]["type"].strip().lower()

    parser_lines: list[str] = []
    call_args: list[str] = []

    for name, raw_type in inputs:
        kind, inner = normalize_type(raw_type)
        if kind == "array":
            length_var = f"{name}Length"
            values_var = f"{name}Values"
            parser_lines.append(f"int {length_var};")
            parser_lines.append(f"cin >> {length_var};")
            parser_lines.append("cin.ignore(numeric_limits<streamsize>::max(), '\\n');")
            parser_lines.append(f"string {values_var};")
            parser_lines.append(f"getline(cin, {values_var});")
            if inner == "int":
                parser_lines.append(f"vector<int> {name};")
                parser_lines.append(f"stringstream {name}Stream({values_var});")
                parser_lines.append(
                    f"for (int i = 0; i < {length_var}; ++i) {{ int value; {name}Stream >> value; {name}.push_back(value); }}"
                )
            elif inner == "bool":
                parser_lines.append(f"vector<bool> {name};")
                parser_lines.append(f"stringstream {name}Stream({values_var});")
                parser_lines.append(
                    f"for (int i = 0; i < {length_var}; ++i) {{ string value; {name}Stream >> value; {name}.push_back(parseBool(value)); }}"
                )
            else:
                parser_lines.append(f"vector<string> {name};")
                parser_lines.append(f"stringstream {name}Stream({values_var});")
                parser_lines.append(
                    f"for (int i = 0; i < {length_var}; ++i) {{ string value; {name}Stream >> value; {name}.push_back(value); }}"
                )
        else:
            if kind == "int":
                parser_lines.append(f"int {name};")
                parser_lines.append(f"cin >> {name};")
            elif kind == "bool":
                parser_lines.append(f"string {name}Raw;")
                parser_lines.append(f"cin >> {name}Raw;")
                parser_lines.append(f"bool {name} = parseBool({name}Raw);")
            else:
                parser_lines.append(f"string {name};")
                parser_lines.append(f"cin >> ws; getline(cin, {name});")
        call_args.append(name)

    result_printer = {
        "int": "cout << result;",
        "bool": "cout << boolToString(result);",
        "str": "cout << result;",
    }.get(result_type, "cout << result;")

    parser_block = "\n".join(f"    {line}" for line in parser_lines)

    return f"""{cpp_helpers()}

<USER_CODE>

int main() {{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

{parser_block}

    auto result = {function_name}({', '.join(call_args)});
    {result_printer}
    return 0;
}}
"""


def cpp_user_boilerplate(schema: dict[str, Any]) -> str:
    inputs = list(schema["input_schema"].items())
    function_name = schema["result"]["function"]
    signature = ", ".join(f"{cpp_type(raw_type)} {name}" for name, raw_type in inputs)
    return f"""#include <bits/stdc++.h>
using namespace std;

{cpp_type(schema['result']['type'])} {function_name}({signature}) {{
    // Write your code here
}}
"""


def build_boilerplates(schema: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {
        "js": {
            "full-js-boilerplate.js": js_full_boilerplate(schema),
            "user-js-boilerplate.js": js_user_boilerplate(schema),
        },
        "cpp": {
            "full-cpp-boilerplate.cpp": cpp_full_boilerplate(schema),
            "user-cpp-boilerplate.cpp": cpp_user_boilerplate(schema),
        },
        "py": {
            "full-py-boilerplate.py": python_full_boilerplate(schema),
            "user-py-boilerplate.py": python_user_boilerplate(schema),
        },
    }


def write_boilerplates(problem_slug: str, boilerplates: dict[str, dict[str, str]]) -> list[Path]:
    written = []
    base_dir = PROBLEM_STATEMENTS_DIR / problem_slug / "boilerplate"
    for language, files in boilerplates.items():
        language_dir = base_dir / language
        language_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            file_path = language_dir / filename
            file_path.write_text(content, encoding="utf-8")
            written.append(file_path)
    return written


def main() -> None:
    problem_slug = get_problem_slug()
    schema = load_schema(problem_slug)
    written = write_boilerplates(problem_slug, build_boilerplates(schema))
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
