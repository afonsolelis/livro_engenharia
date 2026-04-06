#!/usr/bin/env python3
"""
Extract Mermaid and PlantUML diagrams from LaTeX files,
render them as PNG images, and replace lstlisting blocks
with \includegraphics in the .tex files.
"""

import os
import re
import subprocess
import sys
import hashlib

BASE_DIR = "/home/afonsolelis/livro_engenharia"
CHAPTERS_DIR = os.path.join(BASE_DIR, "capitulos")
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
PLANTUML_JAR = os.path.join(BASE_DIR, "tools", "plantuml.jar")

os.makedirs(IMAGES_DIR, exist_ok=True)

# Pattern to match lstlisting blocks that contain diagrams
# We look for lstlisting blocks whose content starts with diagram markers
LSTLISTING_PATTERN = re.compile(
    r'\\begin\{lstlisting\}\[([^\]]*)\]\s*\n(.*?)\\end\{lstlisting\}',
    re.DOTALL
)

def is_mermaid(content):
    """Check if content is a Mermaid diagram."""
    stripped = content.strip()
    mermaid_starts = ['graph ', 'graph\n', 'flowchart ', 'sequenceDiagram',
                      'classDiagram', 'stateDiagram', 'erDiagram',
                      'gantt', 'pie ', 'gitgraph', 'mindmap',
                      'timeline', 'journey', 'quadrantChart',
                      'sankey', 'xychart', 'block-beta']
    return any(stripped.startswith(s) for s in mermaid_starts)

def is_plantuml(content):
    """Check if content is a PlantUML diagram."""
    stripped = content.strip()
    return stripped.startswith('@startuml') or stripped.startswith('@startmindmap') or stripped.startswith('@startwbs')

def extract_caption(options_str):
    """Extract caption from lstlisting options."""
    match = re.search(r'caption\s*=\s*\{([^}]*)\}', options_str)
    if match:
        return match.group(1)
    return None

def extract_label(options_str):
    """Extract label from lstlisting options."""
    match = re.search(r'label\s*=\s*\{([^}]*)\}', options_str)
    if match:
        return match.group(1)
    return None

def sanitize_filename(name):
    """Create a safe filename from a string."""
    # Remove LaTeX commands
    name = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', name)
    name = re.sub(r'\\[a-zA-Z]+', '', name)
    # Transliterate common Portuguese chars
    trans = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e', 'í': 'i', 'ó': 'o',
        'ô': 'o', 'õ': 'o', 'ú': 'u', 'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A',
        'É': 'E', 'Ê': 'E', 'Í': 'I', 'Ó': 'O',
        'Ô': 'O', 'Õ': 'O', 'Ú': 'U', 'Ç': 'C',
    }
    for k, v in trans.items():
        name = name.replace(k, v)
    # Keep only alphanumeric and hyphens
    name = re.sub(r'[^a-zA-Z0-9]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-').lower()
    return name[:60]

def render_mermaid(content, output_path):
    """Render a Mermaid diagram to PNG."""
    tmp_mmd = output_path.replace('.png', '.mmd')
    with open(tmp_mmd, 'w', encoding='utf-8') as f:
        f.write(content.strip())

    try:
        result = subprocess.run(
            ['mmdc', '-i', tmp_mmd, '-o', output_path,
             '-b', 'white', '-w', '1200', '-s', '2'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  WARNING mmdc stderr: {result.stderr[:200]}")
            # Try with puppeteer config for headless
            config_path = output_path.replace('.png', '.json')
            with open(config_path, 'w') as f:
                f.write('{"puppeteerConfig": {"args": ["--no-sandbox"]}}')
            result = subprocess.run(
                ['mmdc', '-i', tmp_mmd, '-o', output_path,
                 '-b', 'white', '-w', '1200', '-s', '2',
                 '-p', config_path],
                capture_output=True, text=True, timeout=30
            )
            if os.path.exists(config_path):
                os.remove(config_path)

        success = os.path.exists(output_path) and os.path.getsize(output_path) > 0
        if os.path.exists(tmp_mmd):
            os.remove(tmp_mmd)
        return success
    except Exception as e:
        print(f"  ERROR rendering Mermaid: {e}")
        if os.path.exists(tmp_mmd):
            os.remove(tmp_mmd)
        return False

def render_plantuml(content, output_path):
    """Render a PlantUML diagram to PNG."""
    tmp_puml = output_path.replace('.png', '.puml')
    with open(tmp_puml, 'w', encoding='utf-8') as f:
        f.write(content.strip())

    try:
        result = subprocess.run(
            ['java', '-jar', PLANTUML_JAR, '-tpng', '-o',
             os.path.dirname(output_path), tmp_puml],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"  WARNING plantuml stderr: {result.stderr[:200]}")

        # PlantUML outputs with same name but .png extension
        expected = tmp_puml.replace('.puml', '.png')
        if expected != output_path and os.path.exists(expected):
            os.rename(expected, output_path)

        success = os.path.exists(output_path) and os.path.getsize(output_path) > 0
        if os.path.exists(tmp_puml):
            os.remove(tmp_puml)
        return success
    except Exception as e:
        print(f"  ERROR rendering PlantUML: {e}")
        if os.path.exists(tmp_puml):
            os.remove(tmp_puml)
        return False

def process_file(tex_path):
    """Process a single .tex file, extracting and rendering diagrams."""
    with open(tex_path, 'r', encoding='utf-8') as f:
        content = f.read()

    chapter_name = os.path.basename(tex_path).replace('.tex', '')
    replacements = []
    diagram_count = 0

    for match in LSTLISTING_PATTERN.finditer(content):
        options = match.group(1)
        body = match.group(2)
        full_match = match.group(0)

        is_mmd = is_mermaid(body)
        is_puml = is_plantuml(body)

        if not is_mmd and not is_puml:
            continue

        diagram_count += 1
        caption = extract_caption(options) or f"Diagrama {diagram_count}"
        label = extract_label(options)
        diagram_type = "mermaid" if is_mmd else "plantuml"

        # Generate filename
        safe_caption = sanitize_filename(caption)
        img_name = f"{chapter_name}-{diagram_count:02d}-{safe_caption}"
        img_filename = f"{img_name}.png"
        img_path = os.path.join(IMAGES_DIR, img_filename)

        print(f"  [{diagram_type.upper()}] {caption[:50]}...")

        if diagram_type == "mermaid":
            success = render_mermaid(body, img_path)
        else:
            success = render_plantuml(body, img_path)

        if success:
            # Build the LaTeX replacement
            label_str = ""
            if label:
                label_str = f"    \\label{{{label}}}\n"

            replacement = (
                f"\\begin{{figure}}[htbp]\n"
                f"    \\centering\n"
                f"    \\includegraphics[width=0.85\\textwidth]{{imagens/{img_filename}}}\n"
                f"    \\caption{{{caption}}}\n"
                f"{label_str}"
                f"\\end{{figure}}"
            )
            replacements.append((full_match, replacement))
            print(f"    -> OK: {img_filename}")
        else:
            print(f"    -> FAILED, keeping as code block")

    # Apply replacements
    if replacements:
        for old, new in replacements:
            content = content.replace(old, new)
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Replaced {len(replacements)} diagrams in {os.path.basename(tex_path)}")

    return len(replacements)

def main():
    total = 0
    tex_files = sorted([f for f in os.listdir(CHAPTERS_DIR) if f.endswith('.tex')])

    for tex_file in tex_files:
        tex_path = os.path.join(CHAPTERS_DIR, tex_file)
        print(f"\n=== Processing {tex_file} ===")
        count = process_file(tex_path)
        total += count

    print(f"\n{'='*50}")
    print(f"Total diagrams rendered: {total}")
    print(f"Images saved to: {IMAGES_DIR}")

if __name__ == '__main__':
    main()
