#!/usr/bin/env python3
"""
NIMH Text Files Metadata Extractor

Extracts metadata and generates semantic tags from NIMH mental health publications.
Outputs consolidated JSON and CSV files.
"""

import os
import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Any


# Tag definitions for content classification
DISORDER_KEYWORDS = {
    "Depression": ["depression", "depressive", "depressed", "sad", "low mood"],
    "Anxiety": ["anxiety", "anxious", "worry", "nervous", "fear"],
    "Bipolar Disorder": ["bipolar", "manic", "mania", "hypomania"],
    "PTSD": ["ptsd", "post-traumatic", "post traumatic", "trauma"],
    "OCD": ["ocd", "obsessive", "compulsive", "unwanted thoughts"],
    "Schizophrenia": ["schizophrenia", "psychosis", "psychotic", "hallucination", "delusion"],
    "ADHD": ["adhd", "attention deficit", "hyperactivity", "inattention"],
    "Autism": ["autism", "asd", "autism spectrum"],
    "Eating Disorders": ["eating disorder", "anorexia", "bulimia", "binge eating"],
    "Panic Disorder": ["panic", "panic attack", "panic disorder"],
    "Social Anxiety": ["social anxiety", "social phobia"],
    "Phobias": ["phobia", "phobias", "specific phobia", "agoraphobia"],
    "Borderline Personality": ["borderline", "bpd", "personality disorder"],
    "Seasonal Affective": ["seasonal affective", "sad", "winter depression"],
    "DMDD": ["dmdd", "disruptive mood", "dysregulation"],
    "Perinatal Depression": ["perinatal", "postpartum", "postnatal", "pregnancy depression"],
    "Suicide Prevention": ["suicide", "suicidal", "self-harm", "crisis"],
    "Stress": ["stress", "stressed", "stressful"],
}

AGE_GROUP_KEYWORDS = {
    "Children": ["children", "child", "kids", "pediatric"],
    "Teens": ["teen", "teens", "teenager", "adolescent", "young adult", "youth"],
    "Adults": ["adult", "adults", "men", "women"],
    "Older Adults": ["older adult", "elderly", "senior", "aging"],
    "General": [],  # Default if no specific age group found
}

CONTENT_TYPE_PATTERNS = {
    "Infographic": ["infographic"],
    "FAQ": ["faq", "frequently asked questions", "questions and answers"],
    "Brochure": ["brochure"],
    "Fact Sheet": ["fact sheet", "what you need to know", "the basics"],
    "Guide": ["guide", "tips", "action steps", "how to"],
}

THEME_KEYWORDS = {
    "Symptoms": ["symptom", "signs", "warning sign"],
    "Treatment": ["treatment", "therapy", "medication", "psychotherapy", "antidepressant"],
    "Diagnosis": ["diagnos", "assessment", "evaluation"],
    "Prevention": ["prevent", "prevention", "protective"],
    "Self-Help": ["self-help", "self-care", "coping", "manage", "take care"],
    "Crisis Support": ["crisis", "hotline", "988", "lifeline", "emergency"],
    "Research": ["research", "clinical trial", "study", "studies"],
    "Genetics": ["gene", "genetic", "hereditary"],
    "Brain Science": ["brain", "neuroscience", "neural"],
}


def extract_header_metadata(content: str) -> Dict[str, str]:
    """Extract TOPIC, TITLE, and SOURCE_URL from file header."""
    metadata = {"topic": "", "title": "", "source_url": ""}
    
    lines = content.split("\n")
    for line in lines[:10]:  # Only check first 10 lines
        line = line.strip()
        if line.startswith("TOPIC:"):
            metadata["topic"] = line[6:].strip()
        elif line.startswith("TITLE:"):
            metadata["title"] = line[6:].strip()
        elif line.startswith("SOURCE_URL:"):
            metadata["source_url"] = line[11:].strip()
    
    return metadata


def detect_language(filename: str, content: str) -> str:
    """Detect if content is in English or Spanish.
    
    Note: All NIMH files are in English. Files with Spanish prefixes
    (like 'Publicaciones_acerca') just have Spanish titles but English content.
    """
    return "English"


def generate_tags(content: str, filename: str) -> Dict[str, Any]:
    """Generate semantic tags based on content analysis."""
    content_lower = content.lower()
    
    # Detect disorders
    disorders = []
    for disorder, keywords in DISORDER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content_lower:
                disorders.append(disorder)
                break
    
    # Detect age groups
    age_groups = []
    for age_group, keywords in AGE_GROUP_KEYWORDS.items():
        if age_group == "General":
            continue
        for keyword in keywords:
            if keyword in content_lower:
                age_groups.append(age_group)
                break
    if not age_groups:
        age_groups = ["General"]
    
    # Detect content type
    content_type = "Fact Sheet"  # Default
    for ctype, patterns in CONTENT_TYPE_PATTERNS.items():
        for pattern in patterns:
            if pattern in content_lower or pattern in filename.lower():
                content_type = ctype
                break
    
    # Detect themes
    themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content_lower:
                themes.append(theme)
                break
    
    # Detect language
    language = detect_language(filename, content)
    
    return {
        "disorders": list(set(disorders)) if disorders else ["General Mental Health"],
        "age_groups": list(set(age_groups)),
        "content_type": content_type,
        "language": language,
        "themes": list(set(themes)) if themes else ["General Information"],
    }


def process_file(filepath: Path) -> Dict[str, Any]:
    """Process a single file and extract all metadata."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Extract header metadata
    header_meta = extract_header_metadata(content)
    
    # Generate tags
    tags = generate_tags(content, filepath.name)
    
    return {
        "filename": filepath.name,
        "topic": header_meta["topic"],
        "title": header_meta["title"],
        "source_url": header_meta["source_url"],
        "tags": tags,
        "file_size_bytes": filepath.stat().st_size,
    }


def main():
    """Main function to process all NIMH text files."""
    # Set up paths
    script_dir = Path(__file__).parent
    nimh_dir = script_dir / "nimh_text_data"
    
    if not nimh_dir.exists():
        print(f"Error: Directory not found: {nimh_dir}")
        return
    
    # Process all text files
    all_metadata = []
    txt_files = list(nimh_dir.glob("*.txt"))
    
    print(f"Processing {len(txt_files)} files...")
    
    for filepath in sorted(txt_files):
        try:
            metadata = process_file(filepath)
            all_metadata.append(metadata)
            print(f"  ✓ {filepath.name}")
        except Exception as e:
            print(f"  ✗ Error processing {filepath.name}: {e}")
    
    # Save JSON output
    json_path = script_dir / "nimh_metadata.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved JSON: {json_path}")
    
    # Save CSV output
    csv_path = script_dir / "nimh_metadata.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow([
            "Filename", "Topic", "Title", "Source URL",
            "Disorders", "Age Groups", "Content Type", "Language", "Themes", "Size (bytes)"
        ])
        # Data rows
        for item in all_metadata:
            writer.writerow([
                item["filename"],
                item["topic"],
                item["title"],
                item["source_url"],
                ", ".join(item["tags"]["disorders"]),
                ", ".join(item["tags"]["age_groups"]),
                item["tags"]["content_type"],
                item["tags"]["language"],
                ", ".join(item["tags"]["themes"]),
                item["file_size_bytes"],
            ])
    print(f"✓ Saved CSV: {csv_path}")
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Total files processed: {len(all_metadata)}")
    
    # Count by disorder
    disorder_counts = {}
    for item in all_metadata:
        for d in item["tags"]["disorders"]:
            disorder_counts[d] = disorder_counts.get(d, 0) + 1
    
    print(f"\nBy Disorder:")
    for disorder, count in sorted(disorder_counts.items(), key=lambda x: -x[1]):
        print(f"  {disorder}: {count}")
    
    # Count by language
    lang_counts = {}
    for item in all_metadata:
        lang = item["tags"]["language"]
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    print(f"\nBy Language:")
    for lang, count in lang_counts.items():
        print(f"  {lang}: {count}")


if __name__ == "__main__":
    main()
