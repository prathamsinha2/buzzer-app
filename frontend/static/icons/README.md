# App Icons

This directory contains the app icons for the PWA. For production, you need to generate proper icons in the following sizes:

- 72x72.png
- 96x96.png
- 128x128.png
- 144x144.png
- 152x152.png
- 192x192.png
- 384x384.png
- 512x512.png

## Quick Icon Generation

You can generate placeholder icons using an online tool or use a design tool like Figma. For development, you can use a simple approach:

### Using ImageMagick (if installed):
```bash
convert -size 512x512 xc:#007AFF -fill white -gravity center -pointsize 200 -annotate +0+0 "B" icon-512x512.png
convert icon-512x512.png -resize 192x192 icon-192x192.png
convert icon-512x512.png -resize 384x384 icon-384x384.png
# ... and so on for other sizes
```

### Recommended Tool:
Use a PWA icon generator: https://www.pwabuilder.com/

## Important for iOS:
- The 192x192 icon will be used for the Home Screen
- Make sure your icon has rounded corners (iOS will add them automatically)
- Use solid colors, avoid transparency for the main icon area
- Test on actual iOS device after uploading

## Files Needed:
Make sure all 8 icon sizes are present before deploying to production.
