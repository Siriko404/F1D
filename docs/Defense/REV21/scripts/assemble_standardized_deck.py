#!/usr/bin/env python3
"""Assemble the explicitly reopened, standardized thesis-defense deck."""

from __future__ import annotations

import base64
import hashlib
import re
import sys
from pathlib import Path

import tinycss2


OUTPUT = Path(
    "/workspace/scratch/5dac4a6a3c28/work/deck-standardized/output/"
    "thesis_defense_main_deck_slides_01-13_standardized_v2.html"
)

NIMBUS_FONT_FILES = {
    (400, "normal"): Path(
        "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Regular.otf"
    ),
    (700, "normal"): Path(
        "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Bold.otf"
    ),
    (400, "italic"): Path(
        "/usr/share/fonts/opentype/urw-base35/NimbusRoman-Italic.otf"
    ),
    (700, "italic"): Path(
        "/usr/share/fonts/opentype/urw-base35/NimbusRoman-BoldItalic.otf"
    ),
}

SLIDES = [
    {
        "number": 1,
        "canonical": "thesis_defense_slide_01_corrected.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_01_corrected(2).html"),
        "sha256": "5f6964197d2864085edf7b294a6fa29abe25ab0660835b29fd6f91947a7d9df1",
        "width": "13.333in",
        "height": "7.5in",
    },
    {
        "number": 2,
        "canonical": "thesis_defense_slide_02_conceptual_framework_I_v2.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_02_conceptual_framework_I_v2(1).html"),
        "sha256": "035b4715157051a4e5d7adeadff1a6c33bb372593daeda6a55c08c17965ebf24",
        "width": "13.333in",
        "height": "7.5in",
    },
    {
        "number": 3,
        "canonical": "thesis_defense_slide_03_conceptual_framework_II_v5.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_03_conceptual_framework_II_v5(1).html"),
        "sha256": "bf337f0a8865606d4d266309a3a113cfba693ea298b95eecb770c9da424ae4b9",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 4,
        "canonical": "thesis_defense_slide_04_research_questions_roadmap_v5.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_04_research_questions_roadmap_v5(1).html"),
        "sha256": "cb582d43b65661888398d9ca741645d239fe41921ce4159662b646e2f9e68197",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 5,
        "canonical": "thesis_defense_slide_05_literature_nearest_work_v4.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_05_literature_nearest_work_v4(1).html"),
        "sha256": "ac2a867cc440d29662b5f5c4c86182224cf16fe7a69d30116bc150feff1fb9fb",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 6,
        "canonical": "thesis_defense_slide_06_data_sample_v6.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_06_data_sample_v6(1).html"),
        "sha256": "342befcc392db62c8d534a369674b2e948d7cf42e8c7b5b20ba194f6117d709a",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 7,
        "canonical": "thesis_defense_slide_07_uncres_measure_v13.html",
        "path": Path("/workspace/scratch/7aa7ca0944b9/upload/thesis_defense_slide_07_uncres_measure_v13(1).html"),
        "sha256": "fb9c7697651678fc1acafb852c03d142a9d3a797bd4ce9c7e4345bbb8bf0914f",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 8,
        "canonical": "thesis_defense_slide_08_preannouncement_runup_v1.html",
        "path": Path("/workspace/scratch/c4e11f39ecf4/work/slide8-final/output/thesis_defense_slide_08_preannouncement_runup_v1.html"),
        "sha256": "bc6c3d89847afc33ec42447f325c9e4ac33e2a1dc3b137e41b8abe8f9fbf326e",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 9,
        "canonical": "thesis_defense_slide_09_announcement_vs_completion_v1.html",
        "path": Path("/workspace/scratch/c4e11f39ecf4/work/slide9-final/output/thesis_defense_slide_09_announcement_vs_completion_v1.html"),
        "sha256": "f5d1d8540e3e5659793c3e09c5bcf572ba757bd92ac8482ca464ca02d07a082b",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 10,
        "canonical": "thesis_defense_slide_10_cash_vs_stock_v1.html",
        "path": Path("/workspace/scratch/c4e11f39ecf4/work/slide10-final/output/thesis_defense_slide_10_cash_vs_stock_v1.html"),
        "sha256": "e93a84e101aa1b673c12922d0c0348a3ffdc48d4a9ce4058c019ba6b3dbff137",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 11,
        "canonical": "thesis_defense_slide_11_contributions_v1.html",
        "path": Path("/workspace/scratch/c4e11f39ecf4/work/slide11-final/output/thesis_defense_slide_11_contributions_v1.html"),
        "sha256": "e77adc5aa9e4364a77658aaf41a7161d1a51c0b7e5118c0cc3d2a583b26ca60b",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 12,
        "canonical": "thesis_defense_slide_12_evidence_boundaries_v1.html",
        "path": Path("/workspace/scratch/5dac4a6a3c28/work/slides12-13-final/output/thesis_defense_slide_12_evidence_boundaries_v1.html"),
        "sha256": "4e1a20b83a35bbcf9a2dbdb38fe90f050c688a7504f15d3102ed444f1c5213e3",
        "width": "16in",
        "height": "9in",
    },
    {
        "number": 13,
        "canonical": "thesis_defense_slide_13_conclusion_v2.html",
        "path": Path("/workspace/scratch/5dac4a6a3c28/work/slides12-13-final/output/thesis_defense_slide_13_conclusion_v2.html"),
        "sha256": "96e7b158c540e346d59f45b5e1a91188420ce69b8c19b2503c3960df9df3d06a",
        "width": "16in",
        "height": "9in",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def embedded_nimbus_font_faces() -> str:
    """Embed one Times-compatible face for the complete standardized deck."""
    faces: list[str] = []
    for (weight, style), path in NIMBUS_FONT_FILES.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required standardized font missing: {path}")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        faces.append(
            "@font-face {"
            "font-family: 'Nimbus Roman Standardized';"
            f"font-style: {style}; font-weight: {weight};"
            f"src: url(data:font/otf;base64,{encoded}) format('opentype');"
            "}"
        )
    return "\n".join(faces)


def standardize_font_resolution(css_text: str) -> str:
    """Resolve every slide to the same embedded Times-compatible face."""
    return css_text.replace(
        '"Times New Roman", Times, serif', '"Nimbus Roman Standardized", serif'
    )


def standardize_font_resolution_in_markup(body: str) -> str:
    """Resolve SVG font-family attributes to the embedded deck face."""
    return body.replace(
        'font-family="Times New Roman, Times, serif"',
        'font-family="Nimbus Roman Standardized"',
    )


def replace_exact(text: str, old: str, new: str, label: str) -> str:
    """Apply an exact approved revision and fail loudly if its anchor drifts."""
    if old not in text:
        raise RuntimeError(f"Revision anchor missing: {label}")
    return text.replace(old, new, 1)


def revise_body(body: str, slide_number: int) -> str:
    """Apply only the user-authorized content/structure revisions."""
    if 2 <= slide_number <= 6:
        body, count = re.subn(
            r'(<div class="page">)\d{2}(</div>)',
            rf'\g<1>{slide_number:02d} / 13\g<2>',
            body,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"Slide {slide_number}: page marker not found")

    if slide_number == 2:
        body = replace_exact(
            body,
            '''        <div class="bottom-cell boundary-wrap">
          <div class="boundary">
            <div class="boundary-label">Boundary</div>
            <div class="boundary-text">The framework predicts the language pattern. It does not identify whether silence is legally constrained or strategically chosen.</div>
          </div>
        </div>
''',
            "",
            "slide 2 boundary panel",
        )
        body = replace_exact(
            body,
            '''    </main>

    <div class="footer">''',
            '''    </main>

    <div class="framework-footnote">Framework note: the prediction concerns the language pattern, not whether silence is legally constrained or strategically chosen.</div>

    <div class="footer">''',
            "slide 2 boundary footnote insertion",
        )

    if slide_number == 4:
        body, count = re.subn(
            r'\s*<div class="tag">Main Analysis [123]</div>', "", body
        )
        if count != 3:
            raise RuntimeError(f"Slide 4: expected three analysis labels, found {count}")
        body = replace_exact(
            body,
            '<div class="spine">Common spine: firm controls, firm fixed effects, year-quarter fixed effects, firm-clustered errors, descriptive interpretation.</div>',
            '''<div class="spine">
      <div class="common-design"><strong>Common design</strong><br>Firm controls; firm and year-quarter fixed effects; firm-clustered errors.</div>
      <div class="boundary-point">All three empirical tests are descriptive within-firm comparisons; they do not identify causal effects.</div>
    </div>''',
            "slide 4 standalone boundary",
        )

    if slide_number == 6:
        body = replace_exact(
            body,
            '<div class="boundary">Boundary: repeated CEO calls and Execucomp coverage tilt the sample toward larger, better-covered firms.</div>',
            '<div class="sample-footnote">Sample note: repeated CEO calls and Execucomp coverage tilt the sample toward larger, better-covered firms.</div>',
            "slide 6 sample footnote",
        )

    if slide_number == 7:
        body = replace_exact(
            body,
            '''  <div class="takeaway"><b>Boundary:</b> UncResCEO is generated in a first-stage decomposition, so the thesis treats two-step estimation uncertainty as a limitation.</div>
  <div class="footer"><span>THESIS TABLE 1 AND DZIELINSKI ET AL. REPLICATION TABLE</span><span>07 / 13</span></div>''',
            '''  <div class="measure-footnote">Measurement note: UncResCEO is generated in a first-stage decomposition; the thesis treats two-step estimation uncertainty as a limitation.</div>
  <div class="footer"><span class="source">Thesis source: Table 1 and Dzielinski et al. replication table.</span><span class="page">07 / 13</span></div>''',
            "slide 7 footnote and footer",
        )

    if slide_number == 8:
        body = replace_exact(
            body,
            '''  <aside class="result-column">
    <div class="result-label">Estimated within-firm shift</div>
    <div class="estimate">+0.0461</div>
    <div class="stat-list">
      <div class="ci">Approx. 95% CI&nbsp; [0.012, 0.080]</div>
      <div>SE&nbsp; 0.0172</div>
      <div>Two-tailed p&nbsp; = 0.0074</div>
    </div>
    <div class="magnitude">''',
            '''  <aside class="result-column">
    <div class="result-label">Estimated within-firm shift</div>
    <div class="stat-grid">
      <div class="stat-metric"><span>Estimate</span><strong class="accent">+0.0461</strong></div>
      <div class="stat-metric"><span>SE</span><strong>0.0172</strong></div>
      <div class="stat-metric"><span>Two-tailed p</span><strong>0.0074</strong></div>
    </div>
    <div class="ci-row">Approx. 95% CI&nbsp; [0.012, 0.080]</div>
    <div class="magnitude">''',
            "slide 8 peer statistics",
        )
        body = replace_exact(
            body,
            '''    <div class="method-item">
      <div class="method-label">Boundary</div>
      <div class="method-value"><strong>Descriptive,<br>not causal</strong></div>
    </div>
''',
            "",
            "slide 8 boundary removal",
        )
        body = body.replace(
            "Approximate 95% CI derived from the reported estimate and SE.</div>",
            "Approximate 95% CI derived from the reported estimate and SE. Note: the estimate is descriptive, not causal.</div>",
            1,
        )

    if slide_number == 9:
        body = body.replace(
            'font-size="18" font-weight="700"',
            'font-size="16.5" font-weight="600"',
        )
        body = replace_exact(
            body,
            '''    <div class="method-item">
      <div class="method-label">Boundary</div>
      <div class="method-value">GAP cash is not significant; persistence rests on no announcement drop. Closing decline partly mechanical. <strong>Descriptive&mdash;not causal; mechanism remains open.</strong></div>
    </div>
''',
            "",
            "slide 9 boundary removal",
        )
        body = body.replace(
            "Approximate 95% CIs derived from reported SEs.</div>",
            "Approximate 95% CIs derived from reported SEs. Note: GAP cash is not significant; the closing decline is partly mechanical; the evidence is descriptive, not causal.</div>",
            1,
        )

    if slide_number == 10:
        body = body.replace(
            'font-size="16.5" font-weight="700"',
            'font-size="15.5" font-weight="600"',
        )
        body = body.replace(
            'font-size="15" font-weight="700" fill="#8F001A">0.0459',
            'font-size="13.7" font-weight="600" fill="#8F001A">0.0459',
            1,
        )
        body = body.replace(
            'font-size="15" font-weight="700" fill="#231F20">-0.0524',
            'font-size="13.7" font-weight="600" fill="#231F20">-0.0524',
            1,
        )
        body = body.replace('font-size="12.7" fill="#6A6461">SE 0.0185', 'font-size="13.2" fill="#6A6461">SE 0.0185', 1)
        body = body.replace('font-size="12.7" fill="#6A6461">SE 0.0436', 'font-size="13.2" fill="#6A6461">SE 0.0436', 1)
        body = replace_exact(
            body,
            '''      <div class="wald-block">
        <div class="wald-label">Direct Wald difference</div>
        <div class="wald-line">
          <div class="wald-name">Cash − Stock</div>
          <div class="wald-value">+0.0983</div>
        </div>
        <div class="wald-stats">SE 0.0476 &nbsp;&middot;&nbsp; approx. 95% CI [0.005, 0.192]<br><span class="sig">Two-tailed p = .039</span></div>
      </div>''',
            '''      <div class="wald-block">
        <div class="wald-label">Direct Wald difference</div>
        <div class="wald-name">Cash − Stock</div>
        <div class="wald-metrics">
          <div><span>Estimate</span><strong class="accent">+0.0983</strong></div>
          <div><span>SE</span><strong>0.0476</strong></div>
          <div><span>Two-tailed p</span><strong>.039</strong></div>
        </div>
        <div class="wald-ci">Approx. 95% CI [0.005, 0.192]</div>
      </div>''',
            "slide 10 peer Wald statistics",
        )
        body = body.replace(
            'Firm-clustered SEs; two-tailed tests. <strong>Within-firm, descriptive; not causal.</strong>',
            'Firm-clustered SEs; two-tailed tests.',
            1,
        )
        body = body.replace(
            "Approximate 95% CIs derived from reported SEs.</div>",
            "Approximate 95% CIs derived from reported SEs. Note: the comparisons are within-firm, descriptive, and not causal.</div>",
            1,
        )

    if slide_number == 11:
        body = replace_exact(
            body,
            '''  <div class="boundary">
    <div>
      <div class="boundary-label">Contribution type</div>
      <div class="boundary-type">Descriptive</div>
    </div>
    <div class="boundary-text">The thesis <strong>characterizes a regularity</strong>; it does not identify a causal channel.</div>
  </div>

''',
            '''  <div class="contribution-footnote">Contribution note: the thesis characterizes a descriptive regularity; it does not identify a causal channel.</div>

''',
            "slide 11 boundary footnote",
        )

    if slide_number == 13:
        body = replace_exact(
            body,
            '      <div class="qa-label">Questions</div>\n',
            "",
            "slide 13 questions label",
        )

    return body


def revision_css(slide_number: int) -> str:
    """Return only the CSS needed for the authorized standardization pass."""
    common_page = ""
    if 3 <= slide_number <= 6:
        common_page = '''
.page { color:#8F001A; font-size:13pt; letter-spacing:0.06em; white-space:nowrap; }
'''

    specific = {
        2: '''
.claim-wrap { width:11.69in; padding-right:0; }
.claim { max-width:8.7in; }
.framework-footnote { position:absolute; left:0.42in; right:0; bottom:0.36in; color:rgba(35,31,32,0.62); font-size:0.112in; line-height:1.14; font-style:italic; }
.page { color:#8F001A; font-size:10.83pt; letter-spacing:0.06em; white-space:nowrap; width:0.68in; }
''',
        4: '''
.equation { padding-top:0.045in; }
.formula { margin-top:0.30in; gap:0.055in 0.085in; }
.chunk { display:inline-block; border:0.9pt solid rgba(35,31,32,0.27); background:transparent; border-radius:0.17in; padding:0.055in 0.12in 0.063in; font-size:15.7pt; }
.chunk.key { border-color:rgba(143,0,26,0.58); background:#EEE6E5; }
.row:nth-child(3) .formula { flex-wrap:nowrap; gap:0.045in; }
.row:nth-child(3) .chunk { font-size:14.35pt; padding-left:0.095in; padding-right:0.095in; }
.spine { bottom:0.64in; display:grid; grid-template-columns:6.68in 6.86in; column-gap:0.42in; justify-content:initial; text-align:left; align-items:start; font-size:12.7pt; line-height:1.14; }
.spine strong { color:#231F20; font-size:10.4pt; letter-spacing:0.12em; text-transform:uppercase; }
.boundary-point { border-left:2.2pt solid #8F001A; padding-left:0.17in; color:#3E3937; }
''',
        6: '''
.boundary { display:none; }
.sample-footnote { position:absolute; left:0.86in; right:0.86in; top:7.79in; color:#6A6461; font-size:10.6pt; line-height:1.14; font-style:italic; }
''',
        7: '''
.takeaway { display:none; }
.measure-footnote { position:absolute; left:0.88in; right:0.88in; bottom:0.66in; color:#6A6461; font-size:10.8pt; line-height:1.14; font-style:italic; }
.footer { color:#6A6461; font-size:11pt; letter-spacing:0; align-items:baseline; }
.footer .source { font-size:11pt; line-height:1.08; }
.footer .page { color:#8F001A; font-size:13pt; letter-spacing:0.06em; white-space:nowrap; }
''',
        8: '''
.stat-grid { display:grid; grid-template-columns:1.48in 1.20in 1.42in; column-gap:0.14in; margin-top:0.19in; }
.stat-metric { min-width:0; }
.stat-metric span { display:block; color:#6A6461; font-size:9.8pt; font-weight:700; letter-spacing:0.10em; text-transform:uppercase; line-height:1.05; white-space:nowrap; }
.stat-metric strong { display:block; margin-top:0.055in; color:#231F20; font-size:20.5pt; line-height:1; font-weight:700; letter-spacing:-0.012em; }
.stat-metric strong.accent { color:#8F001A; }
.ci-row { margin-top:0.17in; color:#4E4946; font-size:15pt; line-height:1.12; }
.magnitude { margin-top:0.22in; padding-top:0.17in; }
.magnitude strong { font-size:22.5pt; }
.method-strip { grid-template-columns:2.72in 8.15in 2.93in; column-gap:0.24in; }
.source { max-width:13.45in; font-size:10.3pt; }
''',
        9: '''
.method-strip { grid-template-columns:2.55in 8.60in 2.65in; column-gap:0.24in; }
.source { max-width:13.45in; font-size:9.7pt; line-height:1.06; }
''',
        10: '''
.wald-name { margin-top:0.035in; font-size:16.2pt; }
.wald-metrics { display:grid; grid-template-columns:1.46in 1.06in 1.37in; column-gap:0.13in; margin-top:0.065in; }
.wald-metrics > div { min-width:0; }
.wald-metrics span { display:block; color:#6A6461; font-size:8.9pt; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; white-space:nowrap; }
.wald-metrics strong { display:block; margin-top:0.025in; color:#231F20; font-size:17.8pt; line-height:1; font-weight:700; }
.wald-metrics strong.accent { color:#8F001A; }
.wald-ci { margin-top:0.055in; color:#4E4946; font-size:11.6pt; line-height:1.08; }
.interpretation { margin-top:0.065in; padding-top:0.075in; }
.source { font-size:9.5pt; line-height:1.05; }
''',
        11: '''
.contribution-footnote { position:absolute; left:0.86in; right:0.86in; bottom:0.67in; color:#6A6461; font-size:11pt; line-height:1.12; font-style:italic; }
''',
        13: '''
.announcement-marker { top:0.57in; margin-left:0; transform:translateX(-50%); }
.announcement-line { transform:translateX(-50%); }
.qa-text { margin-top:0; font-size:21pt; }
''',
    }.get(slide_number, "")
    return common_page + specific


def isolate_inline_svg_classes(body: str, slide_number: int) -> str:
    """Prevent an inline SVG stylesheet from reaching any other deck page."""
    if slide_number != 3:
        return body
    for original in ("label", "small", "big", "note"):
        isolated = f"locked-s03-{original}"
        body = body.replace(f'class="{original}"', f'class="{isolated}"')
        body = body.replace(f".{original} {{", f".{isolated} {{")
    return body


def split_selector_list(selector_text: str) -> list[str]:
    """Split a selector list at top-level commas only."""
    result: list[str] = []
    start = 0
    parens = brackets = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(selector_text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            parens += 1
        elif char == ")":
            parens -= 1
        elif char == "[":
            brackets += 1
        elif char == "]":
            brackets -= 1
        elif char == "," and parens == 0 and brackets == 0:
            result.append(selector_text[start:index].strip())
            start = index + 1
    result.append(selector_text[start:].strip())
    return [item for item in result if item]


def scope_selector(selector: str, prefix: str) -> list[str]:
    normalized = selector.strip()
    if normalized in {"html", "body", ":root"}:
        return [prefix]
    if normalized == "*":
        return [prefix, f"{prefix} *"]

    # Body/root descendants are remapped to the isolated page wrapper.
    remapped = re.sub(r"^(?:html|body|:root)(?=\s|[>+~.#:\[])\s*", "", normalized)
    if remapped != normalized:
        if not remapped:
            return [prefix]
        if remapped[0] in {">", "+", "~", ".", "#", ":", "["}:
            return [f"{prefix}{remapped}"]
        return [f"{prefix} {remapped}"]
    return [f"{prefix} {normalized}"]


def scope_stylesheet(css_text: str, prefix: str) -> str:
    rules = tinycss2.parse_stylesheet(
        css_text, skip_comments=False, skip_whitespace=False
    )
    output: list[str] = []
    for rule in rules:
        if rule.type in {"whitespace", "comment"}:
            output.append(tinycss2.serialize([rule]))
            continue
        if rule.type == "at-rule":
            keyword = rule.lower_at_keyword
            if keyword == "page":
                continue
            prelude = tinycss2.serialize(rule.prelude)
            if rule.content is None:
                output.append(f"@{rule.at_keyword}{prelude};")
            elif keyword in {"media", "supports", "layer", "container"}:
                nested = tinycss2.serialize(rule.content)
                output.append(
                    f"@{rule.at_keyword}{prelude}{{{scope_stylesheet(nested, prefix)}}}"
                )
            else:
                output.append(
                    f"@{rule.at_keyword}{prelude}{{{tinycss2.serialize(rule.content)}}}"
                )
            continue
        if rule.type == "qualified-rule":
            selectors = split_selector_list(tinycss2.serialize(rule.prelude))
            scoped: list[str] = []
            for selector in selectors:
                scoped.extend(scope_selector(selector, prefix))
            output.append(
                f"{', '.join(scoped)}{{{tinycss2.serialize(rule.content)}}}"
            )
            continue
        output.append(tinycss2.serialize([rule]))
    return "".join(output)


def extract_html_parts(text: str, source: Path) -> tuple[list[str], str]:
    head_match = re.search(r"<head\b[^>]*>(.*?)</head>", text, re.I | re.S)
    body_match = re.search(r"<body\b[^>]*>(.*?)</body>", text, re.I | re.S)
    if not head_match or not body_match:
        raise ValueError(f"Could not identify head/body in {source}")
    head_styles = re.findall(
        r"<style\b[^>]*>(.*?)</style>", head_match.group(1), re.I | re.S
    )
    if not head_styles:
        raise ValueError(f"No stylesheet found in {source}")
    return head_styles, body_match.group(1)


def main() -> None:
    scoped_styles: list[str] = []
    page_rules: list[str] = []
    pages: list[str] = []

    for slide in SLIDES:
        source_bytes = slide["path"].read_bytes()
        actual_hash = sha256(source_bytes)
        if actual_hash != slide["sha256"]:
            raise RuntimeError(
                f"Slide {slide['number']} hash mismatch: {actual_hash} != {slide['sha256']}"
            )
        text = source_bytes.decode("utf-8")
        styles, body = extract_html_parts(text, slide["path"])
        body = isolate_inline_svg_classes(body, slide["number"])
        body = revise_body(body, slide["number"])
        body = standardize_font_resolution_in_markup(body)
        prefix = f".deck-page-{slide['number']:02d}"

        page_rules.append(
            f"@page standardized-{slide['number']:02d} {{ "
            "size: 16in 9in; margin: 0; }\n"
            f"{prefix} {{ page: standardized-{slide['number']:02d}; "
            "width: 16in; height: 9in; }"
        )
        for style in styles:
            style = standardize_font_resolution(style)
            scoped_styles.append(
                f"/* Standardized Slide {slide['number']:02d}: {slide['canonical']} */\n"
                + scope_stylesheet(style, prefix)
            )
        local_revision_css = revision_css(slide["number"])
        if local_revision_css:
            scoped_styles.append(
                f"/* Authorized revision overrides for Slide {slide['number']:02d}. */\n"
                + scope_stylesheet(local_revision_css, prefix)
            )

        # The sole inline SVG stylesheet uses uniquely renamed classes and stays local.
        def replace_nested_style(match: re.Match[str]) -> str:
            nested = standardize_font_resolution(match.group(2))
            return match.group(1) + nested + match.group(3)

        body = re.sub(
            r"(<style\b[^>]*>)(.*?)(</style>)",
            replace_nested_style,
            body,
            flags=re.I | re.S,
        )
        pages.append(
            f"<!-- STANDARDIZED SLIDE {slide['number']:02d} | source {slide['canonical']} | "
            f"source SHA-256 {slide['sha256']} -->\n"
            f"<div class=\"deck-page deck-page-{slide['number']:02d}\" "
            f"data-slide-number=\"{slide['number']}\">\n{body.strip()}\n</div>"
        )

    merged = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thesis Defense — Standardized Main Deck, Slides 1–13</title>
<style>
/* One embedded Times-compatible face across the complete deck. */
"""
    merged += embedded_nimbus_font_faces()
    merged += """
html, body { margin: 0; padding: 0; }
body { background: #F4F1EC; }
.deck-page {
  position: relative;
  overflow: hidden;
  margin: 0;
  padding: 0;
  break-after: page;
  page-break-after: always;
}
.deck-page:last-of-type { break-after: auto; page-break-after: auto; }
.deck-page-01 > .slide,
.deck-page-02 > .slide {
  transform: scale(1.2);
  transform-origin: top left;
}
"""
    merged += "\n".join(page_rules)
    merged += "\n\n" + "\n\n".join(scoped_styles)
    merged += "\n</style>\n</head>\n<body>\n"
    merged += "\n\n".join(pages)
    merged += "\n</body>\n</html>\n"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(merged, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"SHA-256 {sha256(OUTPUT.read_bytes())}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
