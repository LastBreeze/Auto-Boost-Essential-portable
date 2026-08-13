import os


def enable_ansi_colors():
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def format_number(value):
    # Keep whole numbers whole so filenames and encoder params stay clean.
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def prompt_number(prompt_text, default, minimum, maximum, integer_only=False):
    """Ask for a number until a valid one is given. Any value in range is accepted."""
    while True:
        raw = input(prompt_text).strip()
        if not raw:
            return format_number(default)

        try:
            value = int(raw) if integer_only else float(raw)
        except ValueError:
            kind = "whole number" if integer_only else "number"
            print(f"  '{raw}' is not a {kind}. Enter a value between {format_number(minimum)} "
                  f"and {format_number(maximum)}, or press Enter for {format_number(default)}.")
            continue

        if value < minimum or value > maximum:
            print(f"  {raw} is outside the allowed range. Enter a value between "
                  f"{format_number(minimum)} and {format_number(maximum)}.")
            continue

        return format_number(value)


# SVT-AV1-Essential names only some presets for --speed. Speed and effort always live in
# FAST_SPEED / FINAL_SPEED, never in FAST_PARAMS / FINAL_PARAMS: a preset without a name is
# written as a bare number (FINAL_SPEED=1) and dispatch.py turns it into --preset for that
# pass. Keeping --preset out of the params leaves the two param strings identical apart
# from photon/film-grain, which is the rule the generated batch file documents.
SPEED_NAMES = {"2": "slower", "4": "slow"}


def params_for_content(crf, luminance_qp_bias, distortion_bias_preset, is_anime):
    crf_param = f"--crf {crf} "
    alt_cdef_param = " --enable-alt-cdef 1" if is_anime else ""
    luminance_param = f" --luminance-qp-bias {luminance_qp_bias}"
    distortion_param = "" if distortion_bias_preset == "0" else f" --distortion-bias-preset {distortion_bias_preset}"

    # Auto-Boost-Av1an-portable SVT-AV1-Essential defaults.
    fast_params = f"{crf_param}--enable-dlf 2{alt_cdef_param}{distortion_param}{luminance_param}"
    final_params = f"{crf_param}--enable-dlf 2{alt_cdef_param}{distortion_param}{luminance_param} --photon-noise 200"

    return fast_params, final_params


def build_batch_script(crf, luminance_qp_bias, distortion_bias_preset, use_avx512, metric_flag, is_anime,
                       preset="4"):
    fast_params, final_params = params_for_content(
        crf, luminance_qp_bias, distortion_bias_preset, is_anime)
    fast_speed = "faster"
    # A named speed where SVT-AV1-Essential has one, otherwise the bare preset number.
    final_speed = SPEED_NAMES.get(preset, preset)
    avx512_flag = "--avx512" if use_avx512 else ""

    script = "@echo off\n"
    script += f'set "FAST_PARAMS={fast_params}"\n'
    script += f'set "FINAL_PARAMS={final_params}"\n'
    script += f'set "FAST_SPEED={fast_speed}"\n'
    script += f'set "FINAL_SPEED={final_speed}"\n'
    script += f'set "AVX512_FLAG={avx512_flag}"\n'
    script += ":: To change quality, edit --crf in both FAST_PARAMS and FINAL_PARAMS so they stay matching.\n"
    script += ":: Leave AVX512_FLAG empty unless you are sure your CPU supports AVX-512.\n"
    script += ":: You can edit this file with Notepad++.\n"
    script += ":: FAST_PARAMS and FINAL_PARAMS must be matching with the exception of photon/film-grain:\n"
    script += ":: Only use --photon-noise or --film-grain in FINAL_PARAMS, adding it to FAST_PARAMS will break metrics.\n"
    script += ":: FAST_SPEED and FINAL_SPEED take either a named speed or a preset number [-1-13]:\n"
    script += "::   slower=2  slow=4  medium=5  fast=6  faster=8. Presets without a name, such as 1,\n"
    script += "::   are written as the number itself. Set the speed here, never --preset in the params.\n"
    if preset not in SPEED_NAMES:
        script += f":: FINAL_SPEED={final_speed} is preset {preset}, which has no name in SVT-AV1-Essential.\n"
    script += "\n"
    script += "setlocal enableextensions disabledelayedexpansion\n"
    script += "cd /d \"%~dp0\"\n"
    script += "del tools\\bat*.txt\n"
    script += "move *.mkv videos-input\n"
    script += "move *.mp4 videos-input\n"
    script += "move *.m2ts videos-input\n"
    script += "cls\n\n"
    script += ":: Create marker\n"
    script += "echo. > \"tools\\bat-used-%~nx0.txt\"\n\n"
    script += ":: Call dispatch.py with parameters\n"
    script += (
        "\"VapourSynth\\python.exe\" \"tools\\dispatch.py\" %AVX512_FLAG% "
        f"{metric_flag} --final-speed %FINAL_SPEED% --fast-speed %FAST_SPEED% "
        "--fast-params \"%FAST_PARAMS%\" --final-params \"%FINAL_PARAMS%\"\n\n"
    )
    script += "echo All tasks finished.\n"
    script += "pause\n"
    return script


def main():
    enable_ansi_colors()
    clear_screen()
    print("================================================")
    print("       Auto-Boost-Essential Batch Builder       ")
    print("================================================\n")
    print("This tool will create a batch script to encode your videos.")
    print("Just answer the questions below and your script will be ready to run.\n")

    print("\n--------------------------------------------------------")
    print("STEP 1 OF 7: Choose a Quality Level (CRF)")
    print("--------------------------------------------------------")
    print("CRF controls the balance between file size and visual quality.")
    print("Lower numbers = higher quality + larger file size.")
    print("Higher numbers = lower quality + smaller file size.\n")
    print("  Recommended starting points:")
    print("    20 -- Very high quality, large files")
    print("    25 -- Good quality, medium files")
    print("    30 -- Lower quality, small files\n")
    print("If you are unsure, start with 30 and adjust from there.")
    print("Any value from 1 to 63 is accepted, not just the ones listed above.")
    print("You can always re-run this tool to generate a new script.\n")
    crf = prompt_number("Enter a CRF value [1-63] (Press Enter to use the default of 30): ", 30, 1, 63)

    print("\n--------------------------------------------------------")
    print("STEP 2 OF 7: Fidelity / Detail Preservation")
    print("--------------------------------------------------------")
    print("This SVT-AV1-Essential setting controls how aggressively the")
    print("encoder preserves fine detail vs. smoothing things out to save space.\n")
    print("  0 -- Default. Balanced. Good for most content. Start here.")
    print("  1 -- Slightly more detail preserved.")
    print("  2 -- Noticeably more detail (may increase file size a bit).")
    print("  3 -- High fidelity. Good for very detailed scenes.")
    print("  4 -- Maximum fidelity. Can significantly increase file size.")
    print("       Mimics SVT-AV1-HDR's tune grain for absolute grain")
    print("       retention with no regard to distortion at all.\n")
    print("Tip: Start at 0. If textures or fine lines look soft or blurry,")
    print("try bumping this up by 1 and compare.\n")
    distortion_bias_preset = prompt_number(
        "Select a fidelity level [0-4] (Press Enter for 0): ", 0, 0, 4, integer_only=True)

    print("\n--------------------------------------------------------")
    print("STEP 3 OF 7: Encoding Speed (Preset)")
    print("--------------------------------------------------------")
    print("This controls how much time and CPU power the encoder spends")
    print("searching for efficient ways to store your video.")
    print("Slower presets = more effort, which usually means better")
    print("quality for the file size (results vary by video).")
    print("Faster presets = quicker encodes, but possibly less efficient")
    print("and less quality.\n")
    print("  Recommended presets for this fork:")
    print("  0 -- Slowest. Maximum effort. Great if you can wait.")
    print("  1 -- Possible slight improvement over preset 2,")
    print("       at the cost of extra encode time.")
    print("  2 -- \"slower\" Very high effort. Still slow, but a good choice")
    print("       for encodes you care about.")
    print("  3 -- Not useful at this time. Offers no significant")
    print("       measurable advantage over preset 4.")
    print("  4 -- \"slow\" DEFAULT. Fastest recommended preset. A solid")
    print("       balance of speed and efficiency. Use this if you")
    print("       have a slower CPU or need results sooner.\n")
    print("  WARNING: Presets faster than 4 are not recommended.")
    print("  They skip many of the tools designed to preserve")
    print("  quality while staying efficient, so output quality")
    print("  will suffer.\n")
    preset = prompt_number(
        "Enter a preset speed [0-4] (Press Enter for the recommended default of 4): ",
        4, 0, 4, integer_only=True)

    print("\n--------------------------------------------------------")
    print("STEP 4 OF 7: Dark Scene Quality Boost")
    print("--------------------------------------------------------")
    print("By default, AV1 treats dark/low-light scenes as less important")
    print("and gives them less detail. This can cause banding or")
    print("blocking or detail loss in shadows and night scenes.")
    print("--luminance-qp-bias counteracts that by boosting quality in")
    print("those darker frames. How strong do you want that boost?\n")
    print("  10 -- Light: a gentle correction, minimal impact on file size, start here")
    print("  30 -- Balanced: solid improvement for most videos")
    print("  50 -- Higher detail: more significant boosting for dark scenes, higher impact on file size\n")
    print("Any value from 0 to 100 is accepted, not just the ones listed above.\n")
    luminance_qp_bias = prompt_number(
        "Enter luminance QP bias [0-100] (Press Enter for 10): ", 10, 0, 100, integer_only=True)

    print("\n--------------------------------------------------------")
    print("STEP 5 OF 7: Quality Metric")
    print("--------------------------------------------------------")
    print("Which metric should Auto-Boost use to measure quality?\n")
    print("  1: SSIMULACRA 2")
    print("     Slower, more accurate.\n")
    print("  2: XPSNR")
    print("     Faster, less accurate.\n")
    metric_choice = input("Select metric (Press Enter for SSIMULACRA 2): ").strip()
    metric_name = "xpsnr" if metric_choice == "2" else "ssim2"
    metric_flag = "" if metric_name == "xpsnr" else "--ssimu2"

    print("\n--------------------------------------------------------")
    print("STEP 6 OF 7: AVX-512 CPU Support")
    print("--------------------------------------------------------")
    print("Some SVT-AV1-Essential builds have an AVX-512 optimized exe.")
    print("Only select Yes if you are sure your CPU supports AVX-512.")
    print("If you are not sure, press Enter for the default: No.\n")
    print("  1: Yes -- Use the AVX-512 optimized encoder executable")
    print("  2: No  -- Use the standard encoder executable\n")
    avx_choice = input("Does your CPU support AVX-512? [1 Yes / 2 No] (Press Enter for No): ").strip()
    use_avx512 = avx_choice == "1"

    print("\n--------------------------------------------------------")
    print("STEP 7 OF 7: Content Type")
    print("--------------------------------------------------------")
    print("What type of content are you encoding?\n")
    print("  1: Anime")
    print("  2: Live action\n")
    content_choice = input("Select content type (Press Enter for Anime): ").strip()
    is_anime = content_choice != "2"

    avx_suffix = "-avx512" if use_avx512 else ""
    content_slug = "anime" if is_anime else "liveaction"
    output_filename = (
        f"batbuilder-{content_slug}-{metric_name}-d{distortion_bias_preset}-crf{crf}-p{preset}{avx_suffix}.bat")
    script = build_batch_script(
        crf, luminance_qp_bias, distortion_bias_preset, use_avx512, metric_flag, is_anime, preset)

    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(root_dir, output_filename)

    with open(file_path, "w", newline="\r\n") as f:
        f.write(script)

    print("\n-------------------------------------------------------------------------------")
    print("Success! Your batch script has been generated:")
    print(f"File: {output_filename}")
    print("-------------------------------------------------------------------------------")
    print("Drop your video files into the 'videos-input' folder, then double-click")
    print("the .bat file to start encoding. Encoded files will appear in 'videos-output'.")
    print("")
    print("Want to tweak the settings manually? Open the .bat file in Notepad++.")
    print("-------------------------------------------------------------------------------")
    os.system("pause")


if __name__ == "__main__":
    main()
