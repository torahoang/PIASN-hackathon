# main.py
import re, sys, os
from rag_engine import setup_rag
from bot_utils import (
    language_detect_and_prompt, citation_from_text,
    grammar_feedback, paraphrase, library_hours, map_link,
    unpack_assignment, triage_resources, peer_language_fallback,
    doc_missing_citations
)

COMMANDS = """
/cite <APA|MLA|IEEE|Vancouver> <doi|url|title>
/proofread <text>
/paraphrase <text>
/hours
/map <building>
/unpack <assignment description>
/resources <visa|health|finance>
/upload <path-to-docx>
"""

def main():
    qa, llm = setup_rag()

    print("📚 ASU Writing Support Chatbot")
    print("Type 'refresh', 'help', or 'exit'.\n")

    while True:
        user_raw = input("You: ").strip()
        if not user_raw:
            continue

        cmd_low = user_raw.lower()

        # meta
        if cmd_low == "exit":
            break
        if cmd_low == "refresh":
            print("🔄 Rebuilding index…")
            qa, llm = setup_rag(refresh=True)
            print("✅ Done!\n")
            continue
        if cmd_low == "help":
            print(COMMANDS)
            continue

        # /cite
        m = re.match(r"/cite\s+(\w+)\s+(.+)", user_raw, re.I)
        if m:
            print("Bot:", citation_from_text(m.group(2), m.group(1)), "\n")
            continue

        # /proofread
        if cmd_low.startswith("/proofread "):
            text = user_raw[11:]
            print("Bot:", grammar_feedback(text, llm), "\n")
            continue

        # /paraphrase
        if cmd_low.startswith("/paraphrase "):
            text = user_raw[12:]
            print("Bot:", paraphrase(text, llm), "\n")
            continue

        # /hours
        if cmd_low == "/hours":
            print("Bot:", library_hours(), "\n")
            continue

        # /map
        m = re.match(r"/map\s+(.+)", user_raw, re.I)
        if m:
            print("Bot: 🗺️", map_link(m.group(1)), "\n")
            continue

        # /unpack
        if cmd_low.startswith("/unpack "):
            desc = user_raw[8:]
            print("Bot:", unpack_assignment(desc, llm), "\n")
            continue

        # /resources
        m = re.match(r"/resources\s+(\w+)", user_raw, re.I)
        if m:
            print("Bot:", triage_resources(m.group(1)), "\n")
            continue

        # /upload
        m = re.match(r"/upload\s+(.+\.docx)", user_raw, re.I)
        if m:
            path = os.path.expanduser(m.group(1))
            if not os.path.isfile(path):
                print("Bot: File not found.\n")
                continue
            offenders = doc_missing_citations(path)
            if offenders:
                print("Bot: Possible uncited quotes:")
                for q in offenders:
                    print(" •", q)
                print()
            else:
                print("Bot: No obvious uncited quotes.\n")
            continue

        # default retrieval
        lang = language_detect_and_prompt(user_raw)
        result = qa({"query": user_raw})["result"]
        club = peer_language_fallback(lang)
        if club:
            result += f"\n\n🔗 You might also connect with a cultural club: {club}"
        print("Bot:", result, "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
