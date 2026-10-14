#!/usr/bin/env node
/**
 * convert_svg.mjs — SVG to PNG converter using sharp
 * Part of the svg-to-png Claude skill
 * Usage: node scripts/convert_svg.mjs --input logo.svg --output logo.png --width 1024
 */

import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

// ── Presets ────────────────────────────────────────────────────────────────
const PRESETS = {
  'app-icon': [
    { width: 1024, height: 1024, name: 'icon-1024', background: '#ffffff' },
    { width: 512,  height: 512,  name: 'icon-512',  background: '#ffffff' },
    { width: 256,  height: 256,  name: 'icon-256',  background: '#ffffff' },
    { width: 128,  height: 128,  name: 'icon-128',  background: '#ffffff' },
    { width: 64,   height: 64,   name: 'icon-64',   background: '#ffffff' },
    { width: 32,   height: 32,   name: 'icon-32',   background: '#ffffff' },
  ],
  'favicon': [
    { width: 256, height: 256, name: 'favicon-256' },
    { width: 128, height: 128, name: 'favicon-128' },
    { width: 64,  height: 64,  name: 'favicon-64'  },
    { width: 32,  height: 32,  name: 'favicon-32'  },
    { width: 16,  height: 16,  name: 'favicon-16'  },
  ],
  'splash-portrait': [
    { width: 1284, height: 2778, name: 'splash-1284x2778' },
    { width: 1170, height: 2532, name: 'splash-1170x2532' },
    { width: 1125, height: 2436, name: 'splash-1125x2436' },
    { width: 828,  height: 1792, name: 'splash-828x1792'  },
    { width: 750,  height: 1334, name: 'splash-750x1334'  },
  ],
  'splash-icon': [
    { width: 1024, height: 1024, name: 'splash-icon-1024' },
  ],
  'og-image': [
    { width: 1200, height: 630, name: 'og-image-1200x630' },
  ],
};

// ── Arg parser ─────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--') || a.startsWith('-')) {
      const key = a.replace(/^-+/, '');
      const aliases = { i:'input', o:'output', w:'width', h:'height', b:'background', p:'preset', d:'output-dir' };
      const resolved = aliases[key] || key;
      args[resolved] = argv[i + 1] && !argv[i + 1].startsWith('-') ? argv[++i] : true;
    }
  }
  return args;
}

// ── SVG viewBox parser ─────────────────────────────────────────────────────
function getViewboxWidth(svgContent) {
  const vb = svgContent.match(/viewBox=["'][\d.]+ [\d.]+ ([\d.]+)/);
  if (vb) return parseFloat(vb[1]);
  const w = svgContent.match(/width=["']([\d.]+)/);
  if (w) return parseFloat(w[1]);
  return 100; // fallback
}

// ── Single conversion ──────────────────────────────────────────────────────
async function convertOne({ inputPath, outputPath, width, height, background }) {
  const svgBuf = fs.readFileSync(inputPath);
  const svgStr = svgBuf.toString();
  const viewboxW = getViewboxWidth(svgStr);

  const targetW = parseInt(width) || 512;
  const targetH = parseInt(height) || targetW;
  const density = Math.round(72 * targetW / viewboxW);

  let pipeline = sharp(svgBuf, { density }).resize(targetW, targetH);

  if (background) {
    pipeline = pipeline.flatten({ background });
  }

  const info = await pipeline.png().toFile(outputPath);
  console.log(`✅ ${outputPath} — ${info.width}×${info.height} (${(info.size / 1024).toFixed(1)}KB)`);
  return info;
}

// ── Preset batch conversion ────────────────────────────────────────────────
async function convertPreset({ inputPath, preset, outputDir, background }) {
  const sizes = PRESETS[preset];
  if (!sizes) {
    console.error(`❌ Unknown preset "${preset}". Available: ${Object.keys(PRESETS).join(', ')}`);
    process.exit(1);
  }

  fs.mkdirSync(outputDir, { recursive: true });
  console.log(`📦 Preset: ${preset} → ${sizes.length} files in ${outputDir}`);

  for (const size of sizes) {
    const bg = background || size.background || null;
    const outPath = path.join(outputDir, `${size.name}.png`);
    await convertOne({
      inputPath,
      outputPath: outPath,
      width: size.width,
      height: size.height,
      background: bg,
    });
  }
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.input) {
    console.error('Usage: node scripts/convert_svg.mjs --input <file.svg> [--output <out.png>] [--width 512] [--height 512] [--background #fff]');
    console.error('       node scripts/convert_svg.mjs --input <file.svg> --preset app-icon --output-dir ./icons');
    process.exit(1);
  }

  if (!fs.existsSync(args.input)) {
    console.error(`❌ Input file not found: ${args.input}`);
    process.exit(1);
  }

  if (args.preset) {
    const outputDir = args['output-dir'] || `./${args.preset}-output`;
    await convertPreset({
      inputPath: args.input,
      preset: args.preset,
      outputDir,
      background: args.background || null,
    });
  } else {
    const outputPath = args.output || args.input.replace(/\.svg$/i, '.png');
    await convertOne({
      inputPath: args.input,
      outputPath,
      width: args.width,
      height: args.height,
      background: args.background || null,
    });
  }
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
