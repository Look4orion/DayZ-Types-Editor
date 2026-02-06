# GitHub Package - Setup Instructions

This package contains everything you need to manage your GitHub repository.

## Files Included

- **.gitignore** - Keeps cache and build files out of git
- **LICENSE** - GPL v3.0 license file
- **README.md** - GitHub repository README (with badges)
- **CHANGELOG.md** - Version history
- **release.bat** - Automated release script
- **update_version.bat** - Version number updater
- All project source code

## Initial Setup (First Time Only)

1. **Extract this package to your project folder**
   - Extract to: `E:\Documents\CrooksEco\TypesEditor\DayZTypesEditor_Complete`
   - Overwrite existing files when prompted

2. **Remove __pycache__ from git** (if you already added files):
   ```bash
   git rm --cached -r __pycache__
   git rm --cached -r config/__pycache__
   git rm --cached -r core/__pycache__
   git rm --cached -r models/__pycache__
   git rm --cached -r ui/__pycache__
   ```

3. **Add all files**:
   ```bash
   git add .
   git commit -m "Release v1.0.1 - Expanded batch operations"
   git push origin main
   ```

## Making Future Releases

### 1. Make Your Changes
Edit code, fix bugs, add features

### 2. Update Version
```bash
update_version.bat
# Enter new version like: 1.0.2
```

### 3. Update CHANGELOG.md
Add new section for your version with changes

### 4. Commit Changes
```bash
git add .
git commit -m "Release v1.0.2 - Description"
git push origin main
```

### 5. Build and Tag
```bash
release.bat
```
This will:
- Build the executable
- Create release zip
- Create git tag
- Push tag to GitHub
- Save zip to `releases/` folder

### 6. Create GitHub Release
1. Go to https://github.com/Look4orion/DayZ-Types-Editor/releases
2. Click "Draft a new release"
3. Select your tag (e.g., v1.0.2)
4. Add release notes from CHANGELOG.md
5. Upload the zip from `releases/` folder
6. Publish

## Quick Reference

**Check status:**
```bash
git status
```

**See what changed:**
```bash
git diff
```

**View commit history:**
```bash
git log --oneline
```

**Undo last commit (keep changes):**
```bash
git reset --soft HEAD~1
```

## Troubleshooting

**Build fails?**
- Make sure all dependencies installed: `pip install -r requirements.txt`
- Check that PyInstaller is installed: `pip install pyinstaller`

**Git push rejected?**
- Pull first: `git pull origin main`
- Then push: `git push origin main`

**Tag already exists?**
- Delete local tag: `git tag -d v1.0.1`
- Delete remote tag: `git push origin :refs/tags/v1.0.1`
- Create new tag: `git tag -a v1.0.1 -m "Version 1.0.1"`
- Push: `git push origin v1.0.1`
