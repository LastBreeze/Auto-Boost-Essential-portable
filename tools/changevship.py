from pathlib import Path
import filecmp
import shutil
import sys


def project_root():
    return Path(__file__).resolve().parent.parent


def get_paths():
    root = project_root()
    libvship_dir = root / "tools" / "libvship"
    plugin_dir = root / "VapourSynth" / "vs-plugins"
    return {
        "root": root,
        "libvship_dir": libvship_dir,
        "plugin_dir": plugin_dir,
        "destination": plugin_dir / "libvship.dll",
        "choices": {
            "1": ("Nvidia", libvship_dir / "libvship_NVIDIA.dll"),
            "2": ("VULKAN (Nvidia/AMD/Intel GPUs)", libvship_dir / "libvship_VULKAN.dll"),
        },
    }


def print_menu():
    print("Auto-Boost-Essential vship plugin selector")
    print("-------------------------------------------")
    print("1. Nvidia")
    print("2. Vulkan (Nvidia/AMD/Intel GPUs)")
    print()


def choose_plugin(choices):
    while True:
        selection = input("Select vship plugin [1-2]: ").strip()
        if selection in choices:
            return choices[selection]
        print("Invalid selection. Please type 1 or 2.")


def copy_plugin(source, destination):
    if not source.exists():
        raise FileNotFoundError(f"Source DLL not found: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and filecmp.cmp(source, destination, shallow=False):
        return "already_active"

    shutil.copy2(source, destination)
    return "copied"


def main():
    paths = get_paths()
    print_menu()
    label, source = choose_plugin(paths["choices"])
    destination = paths["destination"]

    print()
    print(f"Selected: {label}")
    print(f"Source:      {source}")
    print(f"Destination: {destination}")
    print()

    try:
        result = copy_plugin(source, destination)
    except PermissionError:
        print("ERROR: Could not replace libvship.dll because Windows has it locked.")
        print("Close any running Auto-Boost, VapourSynth, vspreview, or Python windows and try again.")
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    if result == "already_active":
        print(f"{label} is already the active vship plugin.")
    else:
        print(f"Copied {source.name} to VapourSynth\\vs-plugins\\libvship.dll")
        print(f"Active vship plugin: {label}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
