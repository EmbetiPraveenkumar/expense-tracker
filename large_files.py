import subprocess

# Get object hash -> filename mapping
objects = subprocess.check_output(
    ["git", "rev-list", "--objects", "--all"],
    text=True
)

object_names = {}

for line in objects.splitlines():
    parts = line.split(" ", 1)
    if len(parts) == 2:
        object_names[parts[0]] = parts[1]

# Read Git pack index
pack_index = r".git\objects\pack\pack-81d723fc2f2062764df04e90fb89233c83568d09.idx"

output = subprocess.check_output(
    ["git", "verify-pack", "-v", pack_index],
    text=True
)

files = []

for line in output.splitlines():
    parts = line.split()

    if len(parts) >= 5 and parts[1] in ("blob", "commit", "tree"):
        object_hash = parts[0]

        try:
            size = int(parts[2])
        except ValueError:
            continue

        filename = object_names.get(object_hash, "[unknown filename]")
        files.append((size, filename))

files.sort(reverse=True)

print("\nLargest Git objects:\n")

for size, filename in files[:30]:
    print(f"{size / (1024 * 1024):8.2f} MB | {filename}")