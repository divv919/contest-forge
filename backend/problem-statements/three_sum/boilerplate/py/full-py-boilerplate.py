def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    return normalized in {"true", "1"}

<USER_CODE>

def main() -> None:
    import sys

    raw_input = sys.stdin.read().rstrip("\n")
    lines = raw_input.splitlines() if raw_input else []
    index = 0

    a = int(lines[index])
    index += 1
    b = int(lines[index])
    index += 1
    c = int(lines[index])
    index += 1

    result = sum_three(a, b, c)
    print(str(result))


if __name__ == "__main__":
    main()
