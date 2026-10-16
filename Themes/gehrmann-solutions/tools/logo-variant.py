#!/usr/bin/env python3
"""Write one colour variant of source/gs-logo.svg with a transparent background.

The source SVG has five layers: transparent, background colour, glow, outline and
shape infill. A variant drops the background layer, recolours outline and infill,
and keeps the glow (in a colour and opacity of its own) or drops it. The viewBox
gets a margin so the glow is not clipped at the edge.

usage: logo-variant.py SOURCE OUT --outline HEX --infill HEX [--glow HEX --glow-opacity F] [--glow-only]
"""
import argparse
import re
import sys

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def colour(value):
    if not HEX.match(value):
        raise argparse.ArgumentTypeError(f"not a #rrggbb colour: {value}")
    return value


def layer(svg, layer_id):
    """Return (start, end) of the <g id=layer_id> element, including its closing tag."""
    start = svg.index(f'id="{layer_id}"')
    start = svg.rindex("<g ", 0, start)
    depth, pos = 0, start
    for match in re.finditer(r"<g\b|</g>", svg[start:]):
        depth += 1 if match.group() == "<g" else -1
        if depth == 0:
            return start, start + match.end()
    sys.exit(f"unbalanced layer {layer_id}")


def recolour(svg, layer_id, fill):
    start, end = layer(svg, layer_id)
    body = re.sub(r'fill="#[0-9a-fA-F]{6}"', f'fill="{fill}"', svg[start:end], count=1)
    return svg[:start] + body + svg[end:]


def drop(svg, layer_id):
    start, end = layer(svg, layer_id)
    return svg[:start] + svg[end:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("out")
    parser.add_argument("--outline", type=colour, required=True)
    parser.add_argument("--infill", type=colour, required=True)
    parser.add_argument("--glow", type=colour)
    parser.add_argument("--glow-opacity", type=float, default=0.75)
    parser.add_argument("--margin", type=int, default=128, help="viewBox margin in SVG units")
    parser.add_argument("--glow-only", action="store_true", help="drop outline and infill (an animation's glow layer)")
    args = parser.parse_args()

    with open(args.source, encoding="utf-8") as f:
        svg = f.read()

    svg = drop(svg, "layer-background")
    svg = recolour(svg, "layer-outline", args.outline)
    svg = recolour(svg, "layer-infill", args.infill)
    if args.glow:
        svg = recolour(svg, "layer-glow", args.glow)
        svg = re.sub(r'(id="layer-glow"[^>]*opacity=")[0-9.]+"', rf'\g<1>{args.glow_opacity}"', svg, count=1)
    else:
        svg = drop(svg, "layer-glow")
    if args.glow_only:
        svg = drop(svg, "layer-outline")
        svg = drop(svg, "layer-infill")

    m = args.margin
    size = 1024 + 2 * m
    svg = re.sub(r'width="1024" height="1024" viewBox="0 0 1024 1024"',
                 f'width="{size}" height="{size}" viewBox="{-m} {-m} {size} {size}"', svg, count=1)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
