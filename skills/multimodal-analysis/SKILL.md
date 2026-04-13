# Skill: Multimodal Product Analysis
ID: `/multimodal`

## Purpose
Allows the AI Agency to analyze product images (from Amare Global or other brands) to extract technical data, verify visual consistency, and estimate pricing using Multimodal Vision AI (Gemini 1.5 Pro / GPT-4o).

## Usage
- **Command**: `/multimodal "ürün fotoğraf analizi"`
- **Context**: Used when a brand image is uploaded or when mapping Media Library assets to product pages.

## Capabilities
1. **Identification**: Detect the exact product name from packaging/labels.
2. **Text Extraction**: OCR (Optical Character Recognition) for ingredients, dosage, and claims shown on the product.
3. **Price Estimation**: Predict pricing based on current market data or provided reference lists.
4. **Visual QA**: Detect broken packaging, low resolution, or incorrect branding.

## Integration
- **Amare Restoration**: Use this skill to map local WordPress Media ID visuals to the correct product ID if filenames are missing.
- **Reels Verification**: Cross-check the product shown in the video foreground with the script content.
