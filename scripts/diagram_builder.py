"""Small native draw.io authoring helper; content/layout remain project decisions."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET


class Page:
    def __init__(self, name, width=1800, height=1200):
        self.name, self.width, self.height, self.counter = name, width, height, 0
        self.model = ET.Element("mxGraphModel", page="1", pageScale="1",
                               pageWidth=str(width), pageHeight=str(height),
                               grid="1", gridSize="10", background="#FFFFFF")
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")

    def _id(self):
        self.counter += 1
        return f"cell-{self.counter}"

    def box(self, label, x, y, width=360, height=140, fill="#EAF2FF",
            stroke="#3B70B8", font=20, shape="rectangle", style=""):
        identifier = self._id()
        store = "size=0.08;spacingTop=28;" if shape == "cylinder" else ""
        properties = (f"shape={shape};rounded=1;html=0;whiteSpace=wrap;"
                      f"fillColor={fill};strokeColor={stroke};strokeWidth=2;"
                      f"fontColor=#152635;fontFamily=Arial;fontSize={font};"
                      f"align=center;verticalAlign=middle;spacing=16;{store}{style}")
        cell = ET.SubElement(self.root, "mxCell", id=identifier, value=label,
                             style=properties, vertex="1", parent="1")
        ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(width),
                      height=str(height), attrib={"as": "geometry"})
        return identifier

    def text(self, label, x, y, width, height=60, font=20):
        return self.box(label, x, y, width, height, font=font,
                        style="fillColor=none;strokeColor=none;align=left;spacing=0;")

    def heading(self, title, kind, scope, question, key):
        self.text(title, 50, 25, self.width - 100, 70, 34)
        self.text(f"{kind} | Scope: {scope}", 50, 105, self.width - 100, 55, 18)
        self.text(question, 50, 175, self.width - 100, 65, 23)
        self.text("KEY " + key, 50, self.height - 100, self.width - 100, 80, 18)

    def boundary(self, label, x, y, width, height):
        identifier = self.box("", x, y, width, height, fill="none",
                              stroke="#8B9AAE", style="rounded=0;dashed=1;")
        self.text(label, x + 20, y + 10, width - 40, 45, 20)
        return identifier

    def edge(self, source, target, label, points=(), ports="", dashed=False,
             arrow="block", label_offset=None):
        identifier = self._id()
        style = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;whiteSpace=nowrap;"
                 f"strokeColor=#273B50;strokeWidth=2;endArrow={arrow};endFill=1;"
                 "fontFamily=Arial;fontSize=18;fontColor=#152635;"
                 f"labelBackgroundColor=#FFFFFF;dashed={int(dashed)};{ports}")
        cell = ET.SubElement(self.root, "mxCell", id=identifier, value=label,
                             source=source, target=target, edge="1", parent="1",
                             style=style)
        geometry = ET.SubElement(cell, "mxGeometry", relative="1", attrib={"as": "geometry"})
        if points:
            array = ET.SubElement(geometry, "Array", attrib={"as": "points"})
            for x, y in points:
                ET.SubElement(array, "mxPoint", x=str(x), y=str(y))
        if label_offset:
            ET.SubElement(geometry, "mxPoint", x=str(label_offset[0]),
                          y=str(label_offset[1]), attrib={"as": "offset"})
        return identifier

    def line(self, x1, y1, x2, y2, label="", dashed=False, arrow="none"):
        identifier = self._id()
        cell = ET.SubElement(self.root, "mxCell", id=identifier, value=label,
                             edge="1", parent="1", style=(
                                 "edgeStyle=none;html=0;whiteSpace=nowrap;"
                                 f"dashed={int(dashed)};endArrow={arrow};"
                                 "strokeColor=#273B50;fontSize=18;fontFamily=Arial;"
                                 "labelBackgroundColor=#FFFFFF;"))
        geometry = ET.SubElement(cell, "mxGeometry", relative="1", attrib={"as": "geometry"})
        for kind, x, y in (("sourcePoint", x1, y1), ("targetPoint", x2, y2)):
            ET.SubElement(geometry, "mxPoint", x=str(x), y=str(y), attrib={"as": kind})
        return identifier

    def lifeline(self, label, x, top=280, bottom=None):
        bottom = self.height - 140 if bottom is None else bottom
        self.box(label, x - 110, top, 220, 90, fill="#FFFFFF", stroke="#8B9AAE",
                 style="rounded=0;")
        self.line(x, top + 90, x, bottom, dashed=True)
        return x

    def message(self, source_x, target_x, y, label, reply=False, asynchronous=False):
        arrow = "open" if reply or asynchronous else "block"
        if source_x == target_x:
            self.line(source_x, y, source_x + 40, y)
            self.line(source_x + 40, y, source_x + 40, y + 28)
            self.line(source_x + 40, y + 28, source_x, y + 28, arrow=arrow)
            self.text(label, source_x + 55, y - 10, 450, 50, 18)
        else:
            self.line(source_x, y, target_x, y, dashed=reply, arrow=arrow)
            self.text(label, min(source_x, target_x) + 15, y - 45,
                      abs(target_x - source_x) - 30, 38, 18)


def write_diagrams(path, pages):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    document = ET.Element("mxfile", host="app.diagrams.net", type="device", compressed="false")
    for index, page in enumerate(pages, 1):
        diagram = ET.SubElement(document, "diagram", id=f"page-{index}", name=page.name)
        diagram.append(deepcopy(page.model))
    ET.indent(document, space="  ")
    ET.ElementTree(document).write(destination, encoding="utf-8", xml_declaration=True)
