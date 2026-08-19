# Restructure site: extract CSS/JS, move images, add 404 and workflow
$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repo

# Create directories
New-Item -ItemType Directory -Force -Path assets\css, assets\js, assets\img, .github\workflows | Out-Null

$path = 'index.html'
if (-not (Test-Path $path)) {
  Write-Error "index.html not found in $repo"
  exit 1
}
$index = Get-Content -Raw $path -ErrorAction Stop

# Extract <style> blocks
$styleMatches = [regex]::Matches($index,'<style\b[^>]*?>(.*?)</style>',[System.Text.RegularExpressions.RegexOptions]::Singleline)
if ($styleMatches.Count -gt 0) {
  $styles = $styleMatches | ForEach-Object { $_.Groups[1].Value }
  $stylesText = $styles -join "`n`n/* ---- STYLE SPLIT ---- */`n`n"
  Set-Content -Path assets\css\main.css -Value $stylesText -Encoding UTF8
  Write-Output "Wrote assets/css/main.css"
} else { Write-Output "No <style> blocks found" }

# Extract inline script blocks (no src)
$scriptMatches = [regex]::Matches($index,'<script\b(?![^>]*\bsrc=)[^>]*?>(.*?)</script>',[System.Text.RegularExpressions.RegexOptions]::Singleline)
if ($scriptMatches.Count -gt 0) {
  $scripts = $scriptMatches | ForEach-Object { $_.Groups[1].Value }
  $scriptsText = $scripts -join "`n`n/* ---- SCRIPT SPLIT ---- */`n`n"
  Set-Content -Path assets\js\main.js -Value $scriptsText -Encoding UTF8
  Write-Output "Wrote assets/js/main.js"
} else { Write-Output "No inline <script> blocks found" }

# Remove all <style>...</style> blocks
$index = [regex]::Replace($index,'<style\b[^>]*?>.*?</style>','',[System.Text.RegularExpressions.RegexOptions]::Singleline)

# Remove known external Tiiny/ad/analytics scripts and asset links
$index = [regex]::Replace($index,'<script[^>]*?(?:tiiny|assets\.tiiny|analytics\.tiiny|tiiny\.host)[^>]*?>.*?</script>','',[System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)
$index = [regex]::Replace($index,'<link[^>]*?(?:assets\.tiiny|f-ui|tiiny\.host)[^>]*?>','',[System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)
# Remove tailwind browser script
$index = [regex]::Replace($index,'<script[^>]*?@tailwindcss\/browser[^>]*?></script>','',[System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)
# Remove plausible/analytics scripts
$index = [regex]::Replace($index,'<script[^>]*(?:plausible|analytics\.tiiny)(?:[^>]*)>.*?</script>','',[System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor [System.Text.RegularExpressions.RegexOptions]::Singleline)

# Replace site_files with assets/img
$index = $index -replace '/site_files/','/assets/img/'

# Remove inline script blocks (we already extracted them)
$index = [regex]::Replace($index,'<script\b(?![^>]*\bsrc=)[^>]*?>.*?</script>','',[System.Text.RegularExpressions.RegexOptions]::Singleline)

# Insert link to external CSS and meta tags after </title>
$metaToInsert = @'
    <link rel="stylesheet" href="/assets/css/main.css">
    <meta property="og:title" content="Swift Talent Recruitment | Premium Talent Acquisition">
    <meta property="og:description" content="Swift Talent Recruitment Company - Expert recruitment in IT, FMCG, Tech, Banking, Consulting &amp; Telecom">
    <meta property="og:image" content="/assets/img/logo-purple-bg.png">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="canonical" href="https://swifttalentrecruitment.com/">
'@
$index = $index -replace '(</title>)',"$1$metaToInsert"

# Ensure we include the new script tag before </body>
if ($index -match '</body>') {
  $index = $index -replace '</body>','    <script src="/assets/js/main.js" defer></script>`n</body>'
} else {
  $index += '`n    <script src="/assets/js/main.js" defer></script>`n'
}

# Write back index
Set-Content -Path $path -Value $index -Encoding UTF8
Write-Output "Updated index.html"

# Move images
$filesToMove = @('SWIFTTALENT.jpg','logo-purple-bg.png')
foreach ($f in $filesToMove) {
  $src = Join-Path 'site_files' $f
  $dst = Join-Path 'assets\img' $f
  if (Test-Path $src) {
    git mv $src $dst | Out-Null
    Write-Output "Moved $f to assets/img"
  }
}

# Create 404.html
$notfound = @'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>404 — Not found</title>
  <link rel="stylesheet" href="/assets/css/main.css">
</head>
<body>
  <main style="padding:48px;max-width:720px;margin:0 auto;text-align:center;">
    <h1>404 — Page not found</h1>
    <p>Sorry, we couldn't find that page.</p>
    <p><a href="/">Return to the homepage</a></p>
  </main>
</body>
</html>
'@
Set-Content -Path 404.html -Value $notfound -Encoding UTF8
Write-Output "Created 404.html"

# Create simple workflow
$workflow = @'
name: HTML Validate

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  html-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install html-validate
        run: |
          npm init -y
          npm install --no-save html-validate@8
      - name: Run html-validate
        run: npx html-validate "index.html" --config-reports-summary
'@
Set-Content -Path .github\workflows\html-validate.yml -Value $workflow -Encoding UTF8
Write-Output "Created workflow"

# Stage and commit
git add -A
$por = git status --porcelain
if ($por) {
  git commit -m "Improve site structure: extract CSS/JS, move images to assets, add 404, add HTML validate workflow" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
} else { Write-Output "No changes to commit" }

# Push
git -c core.sshCommand="ssh -i 'C:\\Users\\Olajide.shittu\\.ssh\\id_ed25519_swifttalentrecruitmentlimited' -o IdentitiesOnly=yes" push origin main
Write-Output "Done"
