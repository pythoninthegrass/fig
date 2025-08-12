#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = [
#     "pictex>=1.1.1",
#     "pyfiglet>=0.8.0",
#     "python-decouple>=3.8",
# ]
# [tool.uv]
# exclude-newer = "2025-08-12T00:00:00Z"
# ///

# pyright: reportMissingImports=false

import os
import pyfiglet
import sys
import tempfile
from decouple import config
from pydoc import pager
from textwrap import dedent


def halp():
    """Programmatically generate well formatted help text for the script"""
    script_name = os.path.basename(sys.argv[0])

    usage = f"Usage:\n\t{script_name} <preview|generate|list> <args...>"

    commands = [
        ("preview <font> <text>", "Preview figlet text with specified font and text"),
        ("generate <font> <text> <file>", "Generate and save figlet text as PNG image"),
        ("list", "List available fonts")
    ]
    commands_text = "Commands:\n" + "\n".join(f"\t{cmd:<39} {desc}" for cmd, desc in commands)

    examples = [
        (script_name, "# Run help (also accepts -h, --help)"),
        (f"{script_name} preview slant", "# Preview slant font with default text"),
        (f"{script_name} preview slant 'Hello'", "# Preview slant font with custom text"),
        (f"{script_name} generate slant 'Hello' out.png", "# Generate PNG image"),
        (f"{script_name} list", "# Show available fonts"),
    ]
    examples_text = "Examples:\n" + "\n".join(f"\t{example:<39} {comment}" for example, comment in examples)

    env_vars = [
        ("FIGLET_FONT", "Default font (default: larry3d)"),
        ("FIGLET_TEXT", "Default text (default: Hello, World!)"),
        ("CANVAS_WIDTH", "Canvas width in pixels (default: 728)"),
        ("CANVAS_HEIGHT", "Canvas height in pixels (default: 90)"),
        ("FONT_COLOR", "Font color (default: black)")
    ]
    env_vars_text = "Environment Variables:\n" + "\n".join(f"\t{var:<39} {desc}" for var, desc in env_vars)

    note_text = dedent(
        """
        Note:
        Generates figlet ASCII art as text preview or PNG images with transparent
        background using PicTex. Default canvas size is 728x90 (leaderboard format)
        with smart cropping enabled.
        """
    ).strip()
    note_text = "\n".join(line if line == "Note:" else f"\t{line}" for line in note_text.split("\n"))

    return "\n\n".join([usage, commands_text, examples_text, env_vars_text, note_text])


def preview(font=None, text=None):
    """Preview figlet text with specified font and text"""
    default_font = config("FIGLET_FONT", default="larry3d")
    default_text = config("FIGLET_TEXT", default="Hello, World!")

    font = font or default_font
    text = text or default_text

    try:
        figlet = pyfiglet.Figlet(font=font)
        result = figlet.renderText(text)
        print(result)
    except Exception as e:
        print(f"Error: {e.__class__.__name__}: {repr(e)}", file=sys.stderr)
        sys.exit(1)


def generate(font=None, text=None, filename=None):
    """Generate figlet text and save as PNG image"""
    from pictex import Canvas, CropMode

    default_font = config("FIGLET_FONT", default="larry3d")
    default_color = config("FONT_COLOR", default="black")
    default_text = config("FIGLET_TEXT", default="Hello, World!")
    default_width = config("CANVAS_WIDTH", default=728, cast=int)
    default_height = config("CANVAS_HEIGHT", default=90, cast=int)

    # Handle case where only filename is provided (args shift left)
    if font and font.endswith('.png') and text is None and filename is None:
        filename = font
        font = None

    font = font or default_font
    text = text or default_text
    filename = filename or "figlet_output.png"

    try:
        figlet = pyfiglet.Figlet(font=font)
        ascii_art = figlet.renderText(text)

        # Create PicTex canvas with monospace font for ASCII art
        canvas = (
            Canvas()
                .font_family("Courier New")
                .font_size(12)
                .color(default_color)
                .background_color("#00000000")
                .padding(20)
                .size(width=default_width, height=default_height)
        )

        # Render ASCII art to image and save with transparent background and smart cropping
        image = canvas.render(ascii_art, crop_mode=CropMode.SMART)
        image.save(filename)

        print(f"Generated PNG image: {filename}")

    except Exception as e:
        print(f"Error: {e.__class__.__name__}: {repr(e)}", file=sys.stderr)
        sys.exit(1)


def list_fonts():
    """List all available figlet fonts"""
    fonts = pyfiglet.FigletFont.getFonts()
    output = ["Available fonts:"]
    output.extend([f"  {font}" for font in sorted(fonts)])

    # Use pager if output is long, otherwise print directly
    full_output = "\n".join(output)
    if len(output) > 30:
        pager(full_output)
    else:
        print(full_output)


def main():
    args = sys.argv[1:]

    # Use pattern matching on the argument structure
    match args:
        # Help cases
        case [] | ["help"] | ["-h"] | ["--help"]:
            print(halp())

        # List fonts
        case ["list"]:
            list_fonts()

        # Explicit command syntax (matches documentation examples)
        case ["preview"]:
            preview(None, None)
        case ["preview", arg]:
            # Smart detection: try as font first, fallback to text if font not found
            try:
                # Test if it's a valid font
                import pyfiglet
                pyfiglet.FigletFont.getFonts()
                if arg in pyfiglet.FigletFont.getFonts():
                    preview(arg, None)
                else:
                    preview(None, arg)
            except Exception:
                preview(None, arg)
        case ["preview", font, text]:
            preview(font, text)
        case ["generate"]:
            generate(None, None, None)
        case ["generate", font]:
            generate(font, None, None)
        case ["generate", font, text]:
            generate(font, text, None)
        case ["generate", font, text, filename]:
            generate(font, text, filename)

        # Implicit syntax (backwards compatibility)
        case [text, filename] if filename.endswith('.png'):
            # fig.py "text" file.png - use default font
            generate(None, text, filename)
        case [font, text, filename] if filename.endswith('.png'):
            # fig.py font "text" file.png - use specified font
            generate(font, text, filename)
        case [filename] if filename.endswith('.png'):
            # fig.py file.png - use all defaults
            generate(None, None, filename)
        case [font]:
            # fig.py font - preview with font and default text
            preview(font, None)
        case [font, text]:
            # fig.py font "text" - preview with font and text
            preview(font, text)

        # Fallback for unexpected patterns
        case _:
            print(f"Unexpected arguments: {args}")
            print(halp())


if __name__ == "__main__":
    main()
