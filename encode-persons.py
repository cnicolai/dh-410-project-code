import argparse
import json
import os
import re
from xml.dom import minidom
from xml.etree import ElementTree as ET
import spacy
from tqdm import tqdm


def load_person_records():
    with open("persons.json", "r") as f:
        return json.load(f)


def find_matching_person(name, person_records):
    for person in person_records:
        if person["name"] == name:
            return person
    return None


def process_text(text, person_records):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    result = text
    # Process entities from back to front to avoid changing the character offsets
    for ent in reversed(doc.ents):
        if ent.label_ == "PERSON":
            person = find_matching_person(ent.text, person_records)
            if person and "tei" in person:
                result = result[: ent.start_char] + person["tei"] + result[ent.end_char :]
    return result


def create_tei_structure():
    tei = ET.Element("TEI", {"xmlns": "http://www.tei-c.org/ns/1.0"})

    # Add the header
    teiHeader = ET.SubElement(tei, "teiHeader")
    fileDesc = ET.SubElement(teiHeader, "fileDesc")

    # Add titleStmt
    titleStmt = ET.SubElement(fileDesc, "titleStmt")
    title = ET.SubElement(titleStmt, "title")
    title.text = "Aubrey Maturin Novels"

    # Add publicationStmt
    publicationStmt = ET.SubElement(fileDesc, "publicationStmt")
    p1 = ET.SubElement(publicationStmt, "p")
    p1.text = "Publication Information"

    # Add sourceDesc
    sourceDesc = ET.SubElement(fileDesc, "sourceDesc")
    p2 = ET.SubElement(sourceDesc, "p")
    p2.text = "Information about the source"

    # Add text and body elements
    text = ET.SubElement(tei, "text")
    body = ET.SubElement(text, "body")
    return tei, body


def extract_book_chapter(filename):
    match = re.match(r"AM(\d+)-(\d+)\.txt", filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def create_paragraph_element(text):
    # Create a properly formatted XML string
    xml_string = f"<p>{text}</p>"
    try:
        # Parse the paragraph text as XML
        return ET.fromstring(xml_string)
    except ET.ParseError:
        # Fallback for pure text content
        p = ET.Element("p")
        p.text = text
        return p


def get_xml_document(text):
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_model1 = '<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>\n'
    xml_model2 = '<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>\n'

    # Get the TEI content
    tei_content = ET.tostring(text, "unicode", method="xml")

    # Combine all parts
    return xml_declaration + xml_model1 + xml_model2 + tei_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Replace person names with TEI tags and create a single XML output."
    )
    parser.add_argument(
        "--path",
        default="/Users/christoph/Library/Mobile Documents/com~apple~CloudDocs/Action/Aubrey Maturin/Chapter/",
        help="Path to the corpus directory",
    )
    args = parser.parse_args()

    # Load person records from JSON created in step 1
    person_records = load_person_records()

    # Create TEI structure
    tei, body = create_tei_structure()

    # Process files and organize by book
    files_info = [
        (f, *extract_book_chapter(f)) for f in os.listdir(args.path) if f.endswith(".txt")
    ]
    # if needed, sort by book number, then chapter
    files_info.sort(key=lambda x: (x[1], x[2]))

    current_book = None
    book_div = None

    for filename, book_num, chapter_num in tqdm(files_info, desc="Processing files"):
        if book_num != current_book:
            current_book = book_num
            book_div = ET.SubElement(body, "div", {"type": "book", "n": str(book_num)})

        chapter_div = ET.SubElement(
            book_div, "div", {"type": "chapter", "n": str(chapter_num)}
        )

        with open(os.path.join(args.path, filename), "r") as file:
            text = file.read()
            # augment person names with TEI tags
            processed_text = process_text(text, person_records)

            # Split into paragraphs and add them to the chapter. Unclear whether all paragraphs are separated by two newlines,
            # but this approximation should work for most cases and won't do any damage if it's not the case.
            paragraphs = processed_text.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    p = create_paragraph_element(para.strip())
                    chapter_div.append(p)

    # Write the complete XML file
    output_path = os.path.join(os.path.dirname(args.path), "aubrey-maturin.xml")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(get_xml_document(tei))
