# Skill: RAG Pipeline Testing
ID: `/test-ai`

## Purpose
Ensures the reliability and truthfulness of responses generated using the system's memory and knowledge base. Specifically targets the "Retrieval-Augmented Generation" flow to prevent hallucinations and maintain brand voice.

## Usage
- **Command**: `/test-ai "RAG pipeline"`
- **Context**: Used during data migration (Amare) and proactive content generation (Dr. Priya) to verify that the retrieved info matches the source.

## Capabilities
1. **Accuracy Test**: Cross-check AI-generated product descriptions against the local SQLite `memory.db` or source JSON files.
2. **Consistency Check**: Verify that information provided to user A matches the info provided to user B for the same query.
3. **Source Attribution**: Audit script segments to ensure they correctly cite scientific studies or internal product data retrieved via RAG.
4. **Hallucination Detection**: Flag instances where the AI adds features or benefits not found in the source documentation.

## Integration
- **Product Verification**: Run this skill after updating `amarenl.com` pages to ensure the WordPress content matches the scraped product data.
- **Dr. Priya QA**: Verify that the video script only uses health claims backed by the internal knowledge base.
