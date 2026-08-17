import urllib.request
from PIL import Image
import io
import html
import pyfiglet

def generate_svg():
    # 1. Fetch the user's avatar
    url = "https://github.com/Hour-Meng.png"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        img_data = response.read()

    # 2. Process image into ASCII art
    img = Image.open(io.BytesIO(img_data)).convert('L')
    # Resize to fit terminal window (adjust for character aspect ratio ~ 1:2)
    img = img.resize((45, 20))

    chars = " .:-=+*#%@"
    ascii_art = ""
    for y in range(img.height):
        line = ""
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            line += chars[pixel * len(chars) // 256]
        # Use tspan for correct alignment and spacing in SVG, and preserve whitespace
        ascii_art += f"<tspan x='0' dy='1.2em'>{html.escape(line)}</tspan>\n"

    # 3. Generate ASCII name with 3D slant style
    name_ascii = pyfiglet.figlet_format("HOUR MENG", font="standard")

    name_lines = name_ascii.split('\n')
    name_tspan = ""
    for line in name_lines:
        if line.strip() or line: # Include empty lines to maintain shape
            name_tspan += f"<tspan x='0' dy='1.2em'>{html.escape(line)}</tspan>\n"

    # 4. Construct the SVG
    svg = f"""<svg width="850" height="400" xmlns="http://www.w3.org/2000/svg">
  <style>
    .ascii-text {{ font-family: 'Courier New', Courier, monospace; font-size: 13px; fill: #8b949e; font-weight: bold; white-space: pre; }}
    .name-text {{ font-family: 'Courier New', Courier, monospace; font-size: 14px; fill: #58a6ff; font-weight: bold; white-space: pre; }}
    .terminal-window {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 8; }}
    .terminal-header {{ fill: #161b22; rx: 8; }}
    .dot {{ r: 6; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .rotate-container {{
      transform-origin: 50% 50%;
      animation: rotate-x 4s ease-in-out infinite alternate;
    }}
    /* The user specified: rotating in x axis -25 degree on both side */
    @keyframes rotate-x {{
      0% {{ transform: perspective(800px) rotateX(-25deg); }}
      100% {{ transform: perspective(800px) rotateX(25deg); }}
    }}
  </style>

  <!-- Background is transparent to fit nicely into README -->

  <rect x="0" y="0" width="850" height="400" class="terminal-window"/>
  <path d="M 0 8 Q 0 0 8 0 L 842 0 Q 850 0 850 8 L 850 30 L 0 30 Z" class="terminal-header" />

  <!-- Terminal dots -->
  <circle cx="20" cy="15" class="dot dot-red"/>
  <circle cx="40" cy="15" class="dot dot-yellow"/>
  <circle cx="60" cy="15" class="dot dot-green"/>
  <text x="425" y="20" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" fill="#8b949e" text-anchor="middle">Terminal Identity</text>
  <text x="425" y="380" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="12" fill="#8b949e" text-anchor="middle">guest@github: ~$ ./portrait.sh</text>

  <g transform="translate(40, 60)">
    <text class="ascii-text" xml:space="preserve">
{ascii_art}
    </text>
  </g>

  <!-- Wrapping name in an inner container for rotation -->
  <g transform="translate(380, 110)">
    <g class="rotate-container">
        <text class="name-text" xml:space="preserve">
{name_tspan}
        </text>
    </g>
  </g>
</svg>
"""

    with open("terminal_identity.svg", "w") as f:
        f.write(svg)
    print("Generated terminal_identity.svg")

if __name__ == "__main__":
    generate_svg()
