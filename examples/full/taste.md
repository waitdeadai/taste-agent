# Taste — Full Example (Smoothrevenue.com)

## 1. Visual Theme & Atmosphere
Dark institutional elegance meets technical precision. Not AI-startup hype. Corporate, serious, trustworthy. The visitor should think "these people have done this 100 times at enterprise scale." Inspired by Linear, Vercel, Stripe Radar.

Mood: dark, precise, premium, institutional

## 2. Reference Benchmarks
- https://linear.app — "dark glass, precision typography, zero fluff"
- https://stripe.com/radar — "data density without clutter"
- https://claude.ai — "warm AI authority, conversational but precise"

## 3. Color Palette & Roles
| Name | Hex | Role |
|------|-----|------|
| Background | #0a0a0b | Page background (near-black, no pure black) |
| Surface | #111114 | Cards, elevated surfaces |
| Border | #1e1e24 | Subtle glass edges |
| Text Primary | #f0f0f5 | Headings, body (near-white) |
| Text Secondary | #8b8b99 | Muted text |
| Accent Primary | #ff6b35 | CTAs, highlights (orange) |
| Accent Secondary | #3b82f6 | Secondary actions (blue) |
| Success | #22c55e | Success states |

## 4. Typography
- Headings: **Sora** (geometric with personality, NOT Inter which is overused)
- Body: **Inter** (optical sizing, variable — the best body font on the market)
- Mono: **JetBrains Mono** (code blocks)
- Scale: 12/14/16/18/24/32/48/64/80px — exaggerated hierarchy

## 5. Component Standards

### CTA Button
- Primary: bg #ff6b35, white text, rounded-lg, px-6 py-3
- Hover: brightness-110 + shadow-lg
- Active: scale 0.98
- Disabled: opacity 0.5, cursor not-allowed

### Glass Card
- Background: rgba(17,17,20,0.8) + backdrop-filter: blur(20px)
- Border: 1px solid rgba(255,255,255,0.08)
- Border-radius: 16px
- Hover: border-color → rgba(255,107,53,0.3) (orange glow)
- Shadow: 0 4px 24px rgba(0,0,0,0.4)

### Input / Textarea
- Background: #111114
- Border: 1px solid #1e1e24
- Focus: border #ff6b35 + box-shadow 0 0 0 3px rgba(255,107,53,0.15)
- Error: border red + error message below
- Placeholder: #8b8b99

### Badge / Tag
- Small rounded pill
- bg-white/5, text-secondary
- Used for: service tags, certification badges

### Accordion (FAQ)
- Border-bottom: 1px solid #1e1e24
- Chevron rotates 180° on open
- Content fades in
- No background color change on open

## 6. Layout & Spacing
- Section padding: 120px vertical (desktop), 64px (mobile)
- Card padding: 32px
- Grid: 12 columns, 24px gutter
- Max content width: 1280px
- Base unit: 4px
- Generous whitespace — sections very airy

## 7. Copy Voice

### Tone
- Confident, direct, no hedging
- Technical authority without being cold
- Results-oriented: metrics, timelines, guarantees
- Objection handling: address enterprise fears head-on

### Approved Headlines (EN)
- Hero H1: "The Execution Layer for Claude at Enterprise Scale"
- Service: "AI Readiness Assessment" + "Know exactly where your AI initiative stands — before you commit budget."
- Objection: "95% of AI pilots fail. We engineer for the other 5%."

### Approved Headlines (ES)
- Hero H1: "La Capa de Ejecución para Claude a Escala Enterprise"
- Servicio: "Evaluación de Preparación para IA" + "Sepa exactamente dónde steht su iniciativa de IA — antes de comprometer presupuesto."

### Rejected Patterns
- Placeholder/hallmark copy ("we help you achieve your goals")
- Corporate boilerplate ("synergy", "leverage", "world-class")
- Startup hype ("revolutionary", "game-changing")
- Untested generic copy

## 8. Non-Negotiables (Hard Rules)
- NO Tailwind CSS — custom design system only
- NO generic stock photos
- NO gradient backgrounds on glass cards (amateur glassmorphism)
- NO parallax or blob animations
- NO emoji in UI
- NO motion that draws attention to itself
- NO placeholder/hallmark copy

## 9. Agent Prompt Guide
```
Color tokens: --bg: #0a0a0b, --surface: #111114, --accent: #ff6b35
Font: Sora (headings), Inter (body), JetBrains Mono (code)
CTA: orange (#ff6b35), rounded-lg, scale on press
Glass: backdrop-filter: blur(20px) only, rgba(17,17,20,0.8) background
Motion: fade-up on scroll, micro-interactions on hover — NO parallax/blob
Section padding: 120px vertical desktop, 64px mobile
```
