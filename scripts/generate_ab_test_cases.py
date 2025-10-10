#!/usr/bin/env python3
"""Generate Controlled A/B Test Cases with Known Entity Patterns

This script creates test cases with intentionally designed informal/formal name variants
to validate AI entity resolution. Unlike random sampling, this generates controlled
evidence where we know exactly which entities should be correlated.

Usage:
    # Default: 10 images + 5 documents
    python scripts/generate_ab_test_cases.py

    # Custom counts
    python scripts/generate_ab_test_cases.py --images 20 --documents 8

    # Specific output directory
    python scripts/generate_ab_test_cases.py --output-dir data/cases/MY-TEST

The script creates:
1. Documents with intentional name variants (informal vs formal)
2. Images with embedded text containing entity names
3. Ground truth JSON documenting expected correlations
4. Two paired cases with different SHA256 hashes for A/B testing
"""

import argparse
import hashlib
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


# Controlled entity test data
TEST_ENTITIES = {
    'people': [
        {
            'canonical_name': 'Sarah Johnson',
            'informal_variants': ['Sarah', 'Sarah J', 'S. Johnson'],
            'email': 'sarah.johnson@company.com',
            'role': 'HR Manager',
            'organization': 'Acme Corp'
        },
        {
            'canonical_name': 'Paul Boucherat',
            'informal_variants': ['Paul', 'Paul B', 'P. Boucherat'],
            'email': 'paul.boucherat@company.com',
            'role': 'Software Engineer',
            'organization': 'Acme Corp'
        },
        {
            'canonical_name': 'Amy Martin',
            'informal_variants': ['Amy', 'A. Martin'],
            'email': 'amy.martin@company.com',
            'role': 'Team Lead',
            'organization': 'Acme Corp'
        },
        {
            'canonical_name': 'Michael Kicks',
            'informal_variants': ['Michael', 'Mike Kicks', 'M. Kicks'],
            'email': 'michael.kicks@company.com',
            'role': 'Senior Manager',
            'organization': 'Acme Corp'
        },
        {
            'canonical_name': 'Rachel Hemmings',
            'informal_variants': ['Rachel', 'R. Hemmings'],
            'email': 'rachel.hemmings@company.com',
            'role': 'HR Business Partner',
            'organization': 'Acme Corp'
        }
    ]
}


def create_email_document(person_data: dict, use_informal: bool, output_path: Path, doc_num: int):
    """Create a test email document with controlled entity mentions

    Args:
        person_data: Entity data dictionary
        use_informal: Whether to use informal name variant
        output_path: Path to save document
        doc_num: Document number for unique ID
    """
    name = random.choice(person_data['informal_variants']) if use_informal else person_data['canonical_name']
    canonical = person_data['canonical_name']
    email = person_data['email']
    role = person_data['role']

    # Create realistic email content
    content = f"""From: {canonical} <{email}>
To: Team Distribution List <team@company.com>
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Subject: Weekly Team Update

Hi Team,

This is {name} writing to update you on this week's progress.

Key Points:
- Project milestone achieved on schedule
- Team collaboration has been excellent
- {name} will be leading next week's planning session

Please let me know if you have any questions.

Best regards,
{name}
{role} | Acme Corp
{email}


<!-- Document ID: {uuid.uuid4()} -->
<!-- Test entity: {canonical} -->
<!-- Variant used: {name} -->
"""

    # Add random whitespace for unique SHA256
    content += ' ' * random.randint(1, 10) + '\n'
    content += f"\n<!-- Random seed: {random.random()} -->\n"

    with open(output_path, 'w') as f:
        f.write(content)


def create_meeting_notes(people: list, output_path: Path):
    """Create meeting notes mentioning multiple people with mixed name formats

    Args:
        people: List of person data dictionaries
        output_path: Path to save document
    """
    # Pick 3-4 random people
    attendees = random.sample(people, min(4, len(people)))

    # Use mix of formal and informal names
    attendee_names = []
    for person in attendees:
        use_informal = random.choice([True, False])
        name = random.choice(person['informal_variants']) if use_informal else person['canonical_name']
        attendee_names.append((name, person['canonical_name']))

    content = f"""Meeting Notes
Date: {datetime.now().strftime('%Y-%m-%d')}
Location: Conference Room B

Attendees:
"""

    for name, canonical in attendee_names:
        content += f"- {name}\n"

    content += f"""

Agenda:
1. Project Status Review
2. Resource Allocation
3. Next Steps

Discussion Summary:

{attendee_names[0][0]} opened the meeting by reviewing current project status.
{attendee_names[1][0]} provided updates on resource allocation and team capacity.

Action Items:
- {attendee_names[0][0]}: Finalize project timeline
- {attendee_names[1][0]}: Update resource plan
"""

    if len(attendee_names) > 2:
        content += f"- {attendee_names[2][0]}: Review budget allocation\n"

    content += f"""

Next meeting scheduled for next week.

Meeting concluded at 3:30 PM.


<!-- Document ID: {uuid.uuid4()} -->
<!-- Attendees: {', '.join([c for _, c in attendee_names])} -->
"""

    # Add random whitespace
    content += ' ' * random.randint(1, 10) + '\n'

    with open(output_path, 'w') as f:
        f.write(content)


def create_informal_document(output_path: Path):
    """Create a document with only informal name mentions

    Args:
        output_path: Path to save document
    """
    people = TEST_ENTITIES['people']
    person1 = random.choice(people)
    person2 = random.choice([p for p in people if p != person1])

    name1 = random.choice(person1['informal_variants'])
    name2 = random.choice(person2['informal_variants'])

    content = f"""Internal Note
{datetime.now().strftime('%Y-%m-%d')}

Quick update from today's discussion:

{name1} and {name2} met this afternoon to discuss the upcoming project deadline.
{name1} suggested moving the timeline forward by one week.
{name2} agreed to review the proposal and get back with feedback.

Follow-up: {name1} will send detailed timeline to team tomorrow.

Note: This was an informal chat, not an official meeting.


<!-- Document ID: {uuid.uuid4()} -->
<!-- Informal mentions: {person1['canonical_name']}, {person2['canonical_name']} -->
"""

    content += ' ' * random.randint(1, 10) + '\n'

    with open(output_path, 'w') as f:
        f.write(content)


def create_test_image_with_text(text: str, output_path: Path):
    """Create a simple PNG image with embedded text

    Args:
        text: Text to embed in image
        output_path: Path to save image
    """
    # Create blank image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a default font, fallback to built-in
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Draw text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill='black', font=font)

    # Add random metadata for unique SHA256
    meta = PngImagePlugin.PngInfo()
    meta.add_text("test_id", str(random.randint(10000, 99999)))
    meta.add_text("timestamp", str(random.random()))
    meta.add_text("random_data", str(random.getrandbits(256)))

    # Save
    img.save(output_path, "PNG", pnginfo=meta)


def generate_controlled_test_case(
    output_dir: Path,
    document_count: int = 5,
    image_count: int = 10
):
    """Generate a controlled test case with known entity patterns

    Args:
        output_dir: Output directory for test case
        document_count: Number of documents to create
        image_count: Number of images to create
    """
    print(f"\n🧪 GENERATING CONTROLLED TEST CASE")
    print(f"={'=' * 70}")
    print(f"Output: {output_dir}")
    print(f"Documents: {document_count}")
    print(f"Images: {image_count}")

    output_dir.mkdir(parents=True, exist_ok=True)

    people = TEST_ENTITIES['people']

    # Generate documents with varied name formats
    print(f"\n📄 Creating documents...")

    # Document 1-2: Formal emails from 2 different people
    for i in range(min(2, document_count)):
        person = people[i % len(people)]
        doc_path = output_dir / f"test_doc_{i+1:02d}.txt"
        create_email_document(person, use_informal=False, output_path=doc_path, doc_num=i+1)
        print(f"   ✅ {doc_path.name} - Formal email from {person['canonical_name']}")

    # Document 3: Meeting notes with mixed names
    if document_count >= 3:
        doc_path = output_dir / "test_doc_03.txt"
        create_meeting_notes(people, doc_path)
        print(f"   ✅ {doc_path.name} - Meeting notes (mixed name formats)")

    # Document 4-5: Informal notes
    for i in range(3, min(document_count, 5)):
        doc_path = output_dir / f"test_doc_{i+1:02d}.txt"
        create_informal_document(doc_path)
        print(f"   ✅ {doc_path.name} - Informal note")

    # Generate images with entity names in text
    print(f"\n🎨 Creating images with embedded text...")

    for i in range(image_count):
        person = people[i % len(people)]
        use_informal = i % 3 != 0  # 2/3 informal, 1/3 formal

        if use_informal:
            name = random.choice(person['informal_variants'])
        else:
            name = person['canonical_name']

        text = f"Meeting with {name}\n{datetime.now().strftime('%Y-%m-%d')}\nConference Room A"

        img_path = output_dir / f"test_image_{i+1:02d}.png"
        create_test_image_with_text(text, img_path)
        print(f"   ✅ {img_path.name} - Mentions {name} ({'informal' if use_informal else 'formal'})")

    # Generate ground truth JSON
    print(f"\n📋 Creating ground truth documentation...")

    ground_truth = {
        'test_case_info': {
            'generated': datetime.now().isoformat(),
            'document_count': document_count,
            'image_count': image_count,
            'purpose': 'A/B testing AI entity resolution'
        },
        'expected_correlations': {
            'with_ai_resolve': [
                {
                    'entity_name': person['canonical_name'],
                    'variants_used': person['informal_variants'] + [person['canonical_name']],
                    'expected_occurrence_count': f"{2}-{5}",
                    'note': 'AI should resolve all variants to canonical name'
                }
                for person in people
            ],
            'without_ai_resolve': {
                'note': 'String matching will only correlate exact matches, missing informal variants',
                'expected_behavior': 'Lower correlation counts, separate entities for variants'
            }
        },
        'entities': people
    }

    ground_truth_path = output_dir / "GROUND_TRUTH.json"
    with open(ground_truth_path, 'w') as f:
        json.dump(ground_truth, f, indent=2)

    print(f"   ✅ {ground_truth_path.name}")

    print(f"\n✅ CONTROLLED TEST CASE CREATED")
    print(f"={'=' * 70}")
    print(f"\n📁 Location: {output_dir}")
    print(f"📊 Contents:")
    print(f"   - {document_count} documents (mixed formal/informal names)")
    print(f"   - {image_count} images (with embedded entity names)")
    print(f"   - 1 ground truth JSON")
    print(f"\n💡 This test case contains:")
    print(f"   - {len(people)} unique people with known name variants")
    print(f"   - Intentional informal/formal name mixing")
    print(f"   - Expected correlation patterns documented")


def main():
    parser = argparse.ArgumentParser(
        description="Generate controlled A/B test cases with known entity patterns"
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path("data/cases/AB-TEST-CONTROLLED"),
        help='Output directory (default: data/cases/AB-TEST-CONTROLLED)'
    )

    parser.add_argument(
        '--documents',
        type=int,
        default=5,
        help='Number of documents to create (default: 5)'
    )

    parser.add_argument(
        '--images',
        type=int,
        default=10,
        help='Number of images to create (default: 10)'
    )

    args = parser.parse_args()

    generate_controlled_test_case(
        output_dir=args.output_dir,
        document_count=args.documents,
        image_count=args.images
    )

    print(f"\n🚀 Ready for A/B testing!")
    print(f"\nRun pipeline WITHOUT AI resolve:")
    print(f"   uv run evidence-toolkit process-case {args.output_dir} \\")
    print(f"       --case-id CONTROLLED-NO-AI")
    print(f"\nRun pipeline WITH AI resolve:")
    print(f"   uv run evidence-toolkit process-case {args.output_dir} \\")
    print(f"       --case-id CONTROLLED-WITH-AI \\")
    print(f"       --ai-resolve")


if __name__ == "__main__":
    main()
