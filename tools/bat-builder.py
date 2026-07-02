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


def quality_label_from_crf(crf):
    try:
        value = float(crf)
    except ValueError:
        return "custom"

    if value <= 20:
        return "higher"
    if value <= 25:
        return "high"
    if value <= 30:
        return "medium"
    if value <= 35:
        return "low"
    return "lower"


def params_for_content(crf, luminance_qp_bias, distortion_bias_preset):
    try:
        crf_value = float(crf)
    except ValueError:
        crf_value = 30.0

    crf_param = "" if crf_value == 30.0 else f"--crf {crf} "
    luminance_param = f" --luminance-qp-bias {luminance_qp_bias}"
    distortion_param = "" if distortion_bias_preset == "0" else f" --distortion-bias-preset {distortion_bias_preset}"

    # Auto-Boost-Av1an-portable SVT-AV1-Essential CRF 30 defaults.
    # CRF 30 itself is supplied by --quality medium, so --crf is only added for non-30 CRF values.
    fast_params = f"{crf_param}--enable-dlf 3{distortion_param}{luminance_param}"
    final_params = f"{crf_param}--enable-dlf 3{distortion_param}{luminance_param} --lp 3 --photon-noise 200"

    return fast_params, final_params


def build_batch_script(crf, luminance_qp_bias, distortion_bias_preset, use_avx512, metric_flag):
    fast_params, final_params = params_for_content(crf, luminance_qp_bias, distortion_bias_preset)
    quality_label = quality_label_from_crf(crf)
    fast_speed = "faster"
    final_speed = "slow"
    avx512_flag = "--avx512" if use_avx512 else ""

    script = "@echo off\n"
    script += f'set "FAST_PARAMS={fast_params}"\n'
    script += f'set "FINAL_PARAMS={final_params}"\n'
    script += f'set "FAST_SPEED={fast_speed}"\n'
    script += f'set "FINAL_SPEED={final_speed}"\n'
    script += f'set "QUALITY={quality_label}"\n'
    script += f'set "AVX512_FLAG={avx512_flag}"\n'
    script += ":: Leave AVX512_FLAG empty unless you are sure your CPU supports AVX-512.\n\n"
    script += ":: Only use --photon-noise or --film-grain in FINAL_PARAMS, adding it to FAST_PARAMS will break metrics.\n\n"
    script += ":: crf to quality guide:\n"
    script += ":: 40 lower\n"
    script += ":: 35 low\n"
    script += ":: 30 medium\n"
    script += ":: 25 high\n"
    script += ":: 20 higher\n"
    script += "del tools\\bat*.txt\n"
    script += "move *.mkv videos-input\n"
    script += "move *.mp4 videos-input\n"
    script += "move *.m2ts videos-input\n"
    script += "cls\n"
    script += "setlocal enableextensions disabledelayedexpansion\n"
    script += "cd /d \"%~dp0\"\n\n"
    script += ":: Create marker\n"
    script += "echo. > \"tools\\bat-used-%~nx0.txt\"\n\n"
    script += ":: Call dispatch.py with parameters\n"
    script += (
        "\"VapourSynth\\python.exe\" \"tools\\dispatch.py\" %AVX512_FLAG% --quality %QUALITY% "
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
    print("STEP 1 OF 5: Choose a Quality Level (CRF)")
    print("--------------------------------------------------------")
    print("CRF controls the balance between file size and visual quality.")
    print("Lower numbers = higher quality + larger file size.")
    print("Higher numbers = lower quality + smaller file size.\n")
    print("  Recommended starting points:")
    print("    20 -- Very high quality, large files")
    print("    25 -- Good quality, medium files")
    print("    30 -- Lower quality, small files\n")
    print("If you are unsure, start with 30 and adjust from there.")
    print("You can always re-run this tool to generate a new script.\n")
    crf = input("Enter a CRF value (Press Enter to use the default of 30): ").strip()
    if not crf:
        crf = "30"

    try:
        crf_value = float(crf)
        if crf_value < 0:
            raise ValueError
    except ValueError:
        print("\nInvalid CRF value. Using the default of 30.")
        crf = "30"

    print("\n--------------------------------------------------------")
    print("STEP 2 OF 5: Fidelity / Detail Preservation")
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
    distortion_bias_preset = input("Select a fidelity level [0-4] (Press Enter for 0): ").strip()
    if distortion_bias_preset not in ("0", "1", "2", "3", "4"):
        distortion_bias_preset = "0"

    print("\n--------------------------------------------------------")
    print("STEP 3 OF 5: Dark Scene Quality Boost")
    print("--------------------------------------------------------")
    print("By default, AV1 treats dark/low-light scenes as less important")
    print("and gives them less detail. This can cause banding or")
    print("blocking or detail loss in shadows and night scenes.")
    print("--luminance-qp-bias counteracts that by boosting quality in")
    print("those darker frames. How strong do you want that boost?\n")
    print("  20 -- Light: a gentle correction, minimal impact on file size, start here")
    print("  40 -- Balanced: solid improvement for most videos")
    print("  60 -- Higher detail: more significant boosting for dark scenes, higher impact on file size\n")
    luminance_qp_bias = input("Enter luminance QP bias (Press Enter for 20): ").strip()
    if luminance_qp_bias not in ("20", "40", "60"):
        luminance_qp_bias = "20"

    print("\n--------------------------------------------------------")
    print("STEP 4 OF 5: Quality Metric")
    print("--------------------------------------------------------")
    print("Which metric should Auto-Boost use to measure quality?\n")
    print("  1: SSIMULACRA 2")
    print("     Slower, more accurate.\n")
    print("  2: XPSNR")
    print("     Faster, less accurate.\n")
    metric_choice = input("Select metric [1 SSIMULACRA 2 / 2 XPSNR] (Press Enter for SSIMULACRA 2): ").strip()
    metric_name = "xpsnr" if metric_choice == "2" else "ssim2"
    metric_flag = "" if metric_name == "xpsnr" else "--ssimu2"

    print("\n--------------------------------------------------------")
    print("STEP 5 OF 5: AVX-512 CPU Support")
    print("--------------------------------------------------------")
    print("Some SVT-AV1-Essential builds have an AVX-512 optimized exe.")
    print("Only select Yes if you are sure your CPU supports AVX-512.")
    print("If you are not sure, press Enter for the default: No.\n")
    print("  1: Yes -- Use the AVX-512 optimized encoder executable")
    print("  2: No  -- Use the standard encoder executable\n")
    avx_choice = input("Does your CPU support AVX-512? [1 Yes / 2 No] (Press Enter for No): ").strip()
    use_avx512 = avx_choice == "1"

    avx_suffix = "-avx512" if use_avx512 else ""
    output_filename = f"batbuilder-{metric_name}-d{distortion_bias_preset}-crf{crf}{avx_suffix}.bat"
    script = build_batch_script(crf, luminance_qp_bias, distortion_bias_preset, use_avx512, metric_flag)

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
