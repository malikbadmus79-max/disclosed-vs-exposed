"""Phase 8: export paper/paper.md to paper/paper.docx (standard library only; no pandoc or python-docx available).

Handles the Markdown subset the paper uses: #/##/### headings, paragraphs, **bold**, *italic*, `code`, bullet and
numbered lists (two levels), pipe tables, ![](png) images, > blockquotes and --- rules (dropped).
usage: phase8_docx.py [in.md] [out.docx]
"""
import re
import struct
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper" / "paper.md"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "paper" / "paper.docx"
FONT = "Calibri"
TEXT_W = 9026  # A4 width 11906 minus 2 x 1440 margins, in DXA
EMU_PER_DXA = 635

images = []  # (rid, filename, bytes)
num_instances = []  # list of (abstract id) per list instance


def runs(text):
    """Inline markdown -> w:r elements."""
    out = []
    for tok in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*)", text):
        if not tok:
            continue
        props = ""
        if tok.startswith("**") and tok.endswith("**"):
            tok, props = tok[2:-2], "<w:b/>"
        elif tok.startswith("`") and tok.endswith("`"):
            tok, props = tok[1:-1], '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="19"/>'
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            tok, props = tok[1:-1].replace("`", ""), "<w:i/>"
        # nested italics inside bold, e.g. **text *x***: strip stray markers
        tok = tok.replace("**", "")
        rpr = f"<w:rPr>{props}</w:rPr>" if props else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(tok)}</w:t></w:r>')
    return "".join(out)


def para(text, style=None, num=None, extra_ppr=""):
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if num:
        ppr += f'<w:numPr><w:ilvl w:val="{num[1]}"/><w:numId w:val="{num[0]}"/></w:numPr>'
    ppr += extra_ppr
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs(text)}</w:p>"


def png_size(b):
    w, h = struct.unpack(">II", b[16:24])
    return w, h


def image(path):
    b = path.read_bytes()
    rid = f"rIdImg{len(images) + 1}"
    images.append((rid, f"image{len(images) + 1}.png", b))
    w, h = png_size(b)
    cx = TEXT_W * EMU_PER_DXA
    cy = int(cx * h / w)
    n = len(images)
    return (f'<w:p><w:pPr><w:jc w:val="center"/><w:keepNext/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{n}" name="Figure {n}"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{n}" name="{path.name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    ncol = max(len(r) for r in cells)
    # column widths proportional to the longest text in each column (min share)
    col = lambda i: [re.sub(r"[*`]", "", r[i]) if i < len(r) else "" for r in cells]
    # weight = longest cell (capped, so prose columns do not starve number columns), never below the longest word
    lens = [max(min(max(len(c) for c in col(i)), 40), max(len(w) for c in col(i) for w in (c.split() or [""])) + 3, 6)
            for i in range(ncol)]
    widths = [int(TEXT_W * l / sum(lens)) for l in lens]
    widths[-1] += TEXT_W - sum(widths)
    border = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="A6A6A6"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    x = [f'<w:tbl><w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:tblBorders>{border}</w:tblBorders>'
         '<w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
         "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"]
    for ri, r in enumerate(cells):
        trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if ri == 0 else "<w:trPr><w:cantSplit/></w:trPr>"
        x.append(f"<w:tr>{trpr}")
        for ci in range(ncol):
            t = r[ci] if ci < len(r) else ""
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="E8EEF7"/>' if ri == 0 else ""
            txt = f"**{t}**" if ri == 0 and t and not t.startswith("**") else t
            x.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[ci]}" w:type="dxa"/>{shade}</w:tcPr>'
                     f'{para(txt, "TableText")}</w:tc>')
        x.append("</w:tr>")
    x.append("</w:tbl>")
    x.append(para("", "TableText"))  # spacer after a table
    return "".join(x)


def new_list(kind):
    num_instances.append(0 if kind == "bullet" else 1)
    return len(num_instances)


def convert(md):
    lines = md.splitlines()
    body, i = [], 0
    cur_list = {}  # kind -> numId while inside a list block
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            # a blank line ends lists unless the next non-blank line continues one
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or not re.match(r"\s*(- |\d+\. )", lines[j]):
                cur_list = {}
            i += 1
            continue
        if s == "---":
            cur_list = {}; i += 1; continue
        m = re.match(r"(#{1,3}) (.*)", s)
        if m:
            cur_list = {}
            lvl = len(m.group(1))
            body.append(para(m.group(2), {1: "Title", 2: "Heading1", 3: "Heading2"}[lvl]))
            i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]); i += 1
            body.append(table(rows)); cur_list = {}; continue
        m = re.match(r"!\[[^\]]*\]\(([^)]+)\)", s)
        if m:
            body.append(image((SRC.parent / m.group(1)).resolve())); i += 1; continue
        if s.startswith("> "):
            body.append(para(s[2:], "Quote")); i += 1; continue
        m = re.match(r"(\s*)(- |\d+\. )(.*)", ln)
        if m:
            indent = len(m.group(1).replace("\t", "    "))
            lvl = 1 if indent >= 2 else 0
            kind = "bullet" if m.group(2) == "- " else "number"
            key = (kind, lvl)
            if lvl == 0:
                # a new top-level list starts when the kind changes
                if key not in cur_list:
                    cur_list = {key: new_list(kind)}
                nid = cur_list[key]
            else:
                if key not in cur_list:
                    cur_list[key] = new_list(kind)
                nid = cur_list[key]
            body.append(para(m.group(3), "ListParagraph", (nid, lvl)))
            i += 1; continue
        # plain paragraph (join soft-wrapped lines)
        buf = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"\s*(#|\||- |\d+\. |>|!\[|---)", lines[i]):
            buf.append(lines[i].strip()); i += 1
        text = " ".join(buf)
        style = "Caption" if re.match(r"\*\*(Figure|Table) \d", text) or (text.startswith("*") and text.endswith("*") and "Source" in text) else None
        body.append(para(text, style)); cur_list = {}
    return "".join(body)


def styles():
    def st(sid, name, rpr, ppr, based="Normal"):
        return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="{based}"/>'
                f'<w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')
    f = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:docDefaults><w:rPrDefault><w:rPr>{f}<w:sz w:val="22"/><w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
            f'<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr>{f}</w:rPr></w:style>'
            + st("Title", "Title", f'{f}<w:b/><w:sz w:val="36"/>', '<w:spacing w:before="0" w:after="200"/><w:keepNext/>')
            + st("Heading1", "heading 1", f'{f}<w:b/><w:sz w:val="30"/><w:color w:val="1F3864"/>', '<w:spacing w:before="360" w:after="120"/><w:keepNext/><w:outlineLvl w:val="0"/>')
            + st("Heading2", "heading 2", f'{f}<w:b/><w:sz w:val="25"/><w:color w:val="1F3864"/>', '<w:spacing w:before="240" w:after="100"/><w:keepNext/><w:outlineLvl w:val="1"/>')
            + st("ListParagraph", "List Paragraph", f, '<w:spacing w:after="60"/>')
            + st("TableText", "Table Text", f'{f}<w:sz w:val="18"/>', '<w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/>')
            + st("Caption", "caption", f'{f}<w:sz w:val="19"/><w:color w:val="404040"/>', '<w:spacing w:before="60" w:after="200"/>')
            + st("Quote", "Quote", f'{f}<w:i/>', '<w:ind w:left="567" w:right="567"/>')
            + "</w:styles>")


def numbering():
    lv = lambda i, fmt, txt, ind: (f'<w:lvl w:ilvl="{i}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/><w:lvlText w:val="{txt}"/>'
                                   f'<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="{ind}" w:hanging="360"/></w:pPr></w:lvl>')
    absb = '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>' + lv(0, "bullet", "•", 720) + lv(1, "bullet", "–", 1440) + "</w:abstractNum>"
    absn = '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>' + lv(0, "decimal", "%1.", 720) + lv(1, "bullet", "–", 1440) + "</w:abstractNum>"
    nums = "".join(f'<w:num w:numId="{k + 1}"><w:abstractNumId w:val="{a}"/>'
                   f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>' for k, a in enumerate(num_instances))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{absb}{absn}{nums}</w:numbering>')


def main():
    md = SRC.read_text(encoding="utf-8")
    body = convert(md)
    sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
           'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
           'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
           f"<w:body>{body}{sect}</w:body></w:document>")
    footer = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
              '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '<Relationship Id="rIdNum" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
            '<Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
            + "".join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{fn}"/>' for rid, fn, _ in images)
            + "</Relationships>")
    ctypes = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
              '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
              '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>')
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
    title = escape(re.search(r"^# (.*)$", md, re.M).group(1))
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>' + title + '</dc:title><dc:creator>Malik Kolawole Badmus</dc:creator></cp:coreProperties>')
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", styles())
        z.writestr("word/numbering.xml", numbering())
        z.writestr("word/footer1.xml", footer)
        z.writestr("word/_rels/document.xml.rels", rels)
        for _, fn, b in images:
            z.writestr(f"word/media/{fn}", b)
    print(f"wrote {OUT} ({len(images)} images, {len(num_instances)} lists, {doc.count('<w:tbl>')} tables)")


if __name__ == "__main__":
    main()
