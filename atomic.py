import subprocess
import sys
from collections import defaultdict


def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Failed: {cmd}")
        sys.exit(result.returncode)


def get_changed_files():
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().split("\n")
    files = []

    for line in lines:
        if not line:
            continue
        path = line[3:]
        files.append(path)

    return files


def group_by_top_level(paths):
    groups = defaultdict(list)
    for path in paths:
        top = path.split("/")[0]
        groups[top].append(path)
    return groups


def main():
    changed = get_changed_files()

    if not changed:
        print("No changes detected.")
        return

    groups = group_by_top_level(changed)

    for group, files in groups.items():
        print(f"Committing group: {group}")

        run("git reset")  # clear staging
        for f in files:
            run(f'git add "{f}"')

        run(f'git commit -m "atomic: update {group}"')

    print("Atomic commits completed.")


if __name__ == "__main__":
    main()