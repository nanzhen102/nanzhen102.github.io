# Profile photo versions

Spare versions of the homepage profile photo. Nothing in this folder is published:
Quartz only builds from `content/`, so these stay in the repo but off the site.

The live photo is `content/profile.jpg`.

## To switch

```bash
cp assets/profile/<version>.jpg content/profile.jpg
```

Then rebuild and check the homepage before pushing.

## Requirements

- Square. It is cropped to a circle, so anything non-square gets cut off.
- 800x800 or larger. Displayed at 220px on desktop, 120px on mobile.
- Face centred, with a little headroom. The circular crop trims the corners.
- JPG, keep it under ~150KB.
