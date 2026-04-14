# Taste — Minimal Example

## 1. Visual Theme & Atmosphere
Clean, modern, professional. Minimal decoration. Every element earns its place.

## 2. Reference Benchmarks
- https://linear.app — precision typography, dark glass
- https://stripe.com — confident, data-driven

## 3. Color Palette
| Name | Hex | Role |
|------|-----|------|
| Background | #0a0a0b | Page background |
| Surface | #111114 | Cards, elevated |
| Accent | #ff6b35 | CTAs, highlights |
| Text | #f0f0f5 | Headings, body |

## 4. Typography
- Headings: **Inter** (optical sizing, variable)
- Body: **Inter** (same family, different weight)

## 5. Copy Voice
Confident, direct, no hedging. Metrics over promises.

### Approved
- "We implement. We operationalize. We deliver."
- "95% of AI pilots fail. We engineer for the other 5%."

### Rejected
- "We help you achieve your goals"
- "synergy", "leverage", "world-class"

## 6. Non-Negotiables
- NO Tailwind CSS
- NO generic stock photos
- NO emoji in UI
- NO gradient backgrounds on glass cards

## 7. Agent Prompt Guide
```
Colors: --bg: #0a0a0b, --accent: #ff6b35
Font: Inter (headings + body)
CTA: #ff6b35, rounded-lg, scale on press
Glass: backdrop-filter: blur(20px) only
```
