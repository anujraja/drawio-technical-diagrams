"""Compare actual draw.io PNG metadata with its native editable source objects."""
import argparse
import base64
import json
from pathlib import Path
import struct
import urllib.parse
import xml.etree.ElementTree as ET
import zlib


def recover_xml(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG")
    offset, embedded, ended = 8, None, False
    while offset + 12 <= len(data):
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        if offset + size + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        crc = struct.unpack(">I", data[offset + 8 + size:offset + 12 + size])[0]
        if zlib.crc32(kind + payload) != crc:
            raise ValueError("Invalid PNG CRC")
        offset += size + 12
        if kind == b"zTXt":
            keyword, contents = payload.split(b"\0", 1)
            if keyword == b"mxGraphModel":
                if not contents or contents[0] != 0:
                    raise ValueError("Unsupported PNG text compression")
                embedded = ET.fromstring(urllib.parse.unquote(zlib.decompress(contents[1:]).decode()))
        if kind == b"IEND":
            ended = True
            break
    if not ended or offset != len(data):
        raise ValueError("Missing PNG end or unexpected trailing bytes")
    if embedded is None:
        raise ValueError("PNG contains no editable draw.io XML")
    return embedded


def normalized(node):
    return (node.tag, sorted(node.attrib.items()), (node.text or "").strip(),
            [normalized(child) for child in node])


def page_cells(document):
    diagrams = document.findall("diagram") if document.tag == "mxfile" else [document]
    pages = []
    for diagram in diagrams:
        model = diagram.find("mxGraphModel") if diagram.tag == "diagram" else diagram
        if model is None and diagram.text:
            model = ET.fromstring(urllib.parse.unquote(
                zlib.decompress(base64.b64decode(diagram.text), -15).decode()))
        if model is None or model.tag != "mxGraphModel":
            raise ValueError("Missing native editable graph model")
        cells = model.findall(".//mxCell")
        identifiers = [cell.get("id") for cell in cells]
        if None in identifiers or len(set(identifiers)) != len(identifiers):
            raise ValueError("Missing or duplicate cell IDs within a page")
        pages.append({cell.get("id"): normalized(cell) for cell in cells})
    if not pages:
        raise ValueError("No diagram pages")
    return pages


def validate(source, png, page=None):
    original = page_cells(ET.parse(source).getroot())
    recovered = page_cells(recover_xml(png))
    if page is not None and not 1 <= page <= len(original):
        raise ValueError("Requested page index is out of range")
    expected = original if recovered == original else (
        [original[page - 1]] if page is not None else original)
    if recovered != expected:
        raise ValueError("PNG native cell trees do not match the source")
    vertices = edges = image_cells = 0
    for cells in recovered:
        for node in cells.values():
            attributes = dict(node[1])
            vertices += attributes.get("vertex") == "1"
            edges += attributes.get("edge") == "1"
            style = attributes.get("style", "")
            image_cells += "shape=image" in style or style.startswith("image;")
    return {"source_pages": len(original), "embedded_pages": len(recovered),
            "editable_shapes_and_text": vertices, "connectors_and_lifelines": edges,
            "image_cells": image_cells, "cell_tree_match": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("png", type=Path)
    parser.add_argument("--page", type=int)
    args = parser.parse_args()
    print(json.dumps(validate(args.source, args.png, args.page), indent=2))


if __name__ == "__main__":
    main()
