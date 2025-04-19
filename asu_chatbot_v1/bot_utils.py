# bot_utils.py
"""
Utility helpers for the ASU Writing Support Chatbot
"""

import re, json, subprocess, requests
from langdetect import detect
from docx import Document

# ──────────────────────────────────────────────────
# 1. Language detection
# ──────────────────────────────────────────────────
def language_detect_and_prompt(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"

# ──────────────────────────────────────────────────
# 2. Inline citation (Crossref)
# ──────────────────────────────────────────────────
STYLE_MAP = {
    "apa": "apa",
    "mla": "mla",
    "ieee": "ieee",
    "vancouver": "vancouver"
}

def citation_from_text(raw: str, style: str = "apa") -> str:
    style = STYLE_MAP.get(style.lower(), "apa")
    doi = (
        raw.split("doi.org/")[-1].lstrip().split()[0]
        if "doi" in raw.lower()
        else raw
    )
    if doi.startswith("https"):
        return "(citation error: not a DOI)"
    url = f"https://api.crossref.org/works/{doi}"
    r = requests.get(url, timeout=8)
    if r.status_code != 200:
        return f"(citation error: Crossref {r.status_code})"
    msg = r.json()["message"]

    # authors
    auths = msg.get("author", [])
    def apa(a): return f"{a['family']}, {a['given'][0]}."
    def mla(a): return f"{a['family']}, {a['given']}"
    def ieee(a):
        initials = "".join([f"{n[0]}." for n in a['given'].split()])
        return f"{initials} {a['family']}"
    def van(a):
        initials = "".join(n[0] for n in a['given'].split())
        return f"{a['family']} {initials}"

    if style == "apa":
        if len(auths) <= 2:
            auth_str = " & ".join(apa(a) for a in auths)
        else:
            auth_str = f"{apa(auths[0])} et al."
    elif style == "mla":
        auth_str = ", and ".join(mla(a) for a in auths[:2]) + \
                   (", et al." if len(auths) > 2 else "")
    elif style == "ieee":
        auth_str = ", ".join(ieee(a) for a in auths)
    else:  # Vancouver
        auth_str = ", ".join(van(a) for a in auths[:6]) + \
                   (" et al." if len(auths) > 6 else "")

    year = msg.get("issued", {}).get("date-parts", [[None]])[0][0] or ""
    title = msg.get("title", [""])[0].rstrip(".")
    journal = msg.get("container-title", [""])[0]
    vol = msg.get("volume", "")
    issue = msg.get("issue", "")
    pages = msg.get("page", "")

    if style == "apa":
        return f"{auth_str} ({year}). {title}. {journal}, {vol}({issue}), {pages}. https://doi.org/{doi}"
    if style == "mla":
        return f"{auth_str}. “{title}.” {journal} {vol}.{issue} ({year}): {pages}."
    if style == "ieee":
        return f"{auth_str}, “{title},” {journal}, vol. {vol}, no. {issue}, pp. {pages}, {year}."
    # Vancouver
    return f"{auth_str}. {title}. {journal}. {year};{vol}({issue}):{pages}."

# ──────────────────────────────────────────────────
# 3. Grammar, Paraphrase, Unpack (plain‑string prompts)
# ──────────────────────────────────────────────────
def grammar_feedback(text: str, llm) -> str:
    prompt = (
        "Improve grammar and clarity of the following passage. "
        "Do NOT change its meaning. Return ONLY the revised passage.\n\n"
        f"{text}\n\nRevised:"
    )
    return llm.invoke(prompt)

def paraphrase(text: str, llm) -> str:
    prompt = (
        "Rewrite the following passage in different words to avoid plagiarism, "
        "but keep the technical meaning the same. "
        "Return ONLY the paraphrased version.\n\n"
        f"{text}\n\nParaphrased:"
    )
    return llm.invoke(prompt)

def unpack_assignment(text: str, llm) -> str:
    prompt = (
        "You are an academic writing coach. "
        "A student gives you an assignment description. "
        "Break it down into: objectives, key action verbs, grading criteria, "
        "and suggested first steps. Use bullet points.\n\n"
        f"Assignment:\n{text}"
    )
    return llm.invoke(prompt)

# ──────────────────────────────────────────────────
# 4. Library hours (with graceful fallback)
# ──────────────────────────────────────────────────
HOURS_URL = "https://lib.asu.edu/about/hours/json"

def library_hours() -> str:
    try:
        rsp = requests.get(HOURS_URL, timeout=6).json()
        today = rsp.get("today", {})
        return f"Today ({today.get('date','–')}): Noble Library is open {today.get('hours','–')}."
    except Exception:
        return "Live hours feed unavailable right now—try again later."

# ──────────────────────────────────────────────────
# 5. Map link
# ──────────────────────────────────────────────────
def map_link(query: str) -> str:
    slug = query.lower().replace(" ", "-")
    return f"https://www.asu.edu/map/interactive/?id={slug}"

# ──────────────────────────────────────────────────
# 6. Resource triage
# ──────────────────────────────────────────────────
TRIAGE = {
    "visa": "https://international.asu.edu/",
    "health": "https://eoss.asu.edu/health",
    "finance": "https://students.asu.edu/financialaid"
}
def triage_resources(topic: str) -> str:
    return TRIAGE.get(topic, "Topic not found. Try visa / health / finance.")

# ──────────────────────────────────────────────────
# 7. Peer‑language clubs
# ──────────────────────────────────────────────────
CLUBS = {
    "hi": "https://asu.campuslabs.com/engage/organization/indo-american",
    "fr": "https://asu.campuslabs.com/engage/organization/frenchclub",
    "es": "https://asu.campuslabs.com/engage/organization/latinobarrett"
}
def peer_language_fallback(code: str) -> str:
    return CLUBS.get(code, "")

# ──────────────────────────────────────────────────
# 8. Missing‑citation checker
# ──────────────────────────────────────────────────
QUOTE_RE = re.compile(r'“([^”]{20,})”')

def doc_missing_citations(path: str) -> list[str]:
    doc = Document(path)
    txt = "\n".join(p.text for p in doc.paragraphs)
    offenders = []
    for quote in QUOTE_RE.findall(txt):
        if "(cite)" in quote.lower():
            continue
        offenders.append(quote[:70] + "…")
    return offenders
