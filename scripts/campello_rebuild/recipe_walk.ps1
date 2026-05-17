<#
.SYNOPSIS
  Deterministic one-paragraph-at-a-time walk of the Campello recipe TSV,
  comparing each row against the existing rebuild to locate the deviation.

.DESCRIPTION
  Strictly sequential. The cursor (cursor.json) advances ONLY when a
  verdict line is appended to walk_verdicts.tsv — you cannot silently
  skip. No interpretation drift: text is the verbatim extractor output.

  recipe_paragraphs.tsv : paragraph_id<TAB>source<TAB>pdf_page<TAB>kind<TAB>text
  cursor.json           : {"current_paragraph_id":N,"total":M}
  walk_verdicts.tsv     : paragraph_id<TAB>verdict<TAB>rebuild_locus<TAB>note

.PARAMETER Verdict
  One of MATCH | DEVIATION | NOT_RECIPE | AMBIGUOUS. Appends a verdict
  line for the CURRENT paragraph, advances the cursor, prints the next.

.PARAMETER Locus
  rebuild file:line(s) compared against (e.g. step2_beta_uk.py:40-70).

.PARAMETER Note
  One-line evidence/justification for the verdict.

.PARAMETER Status
  Print cursor + verdict-count, do nothing else.

.EXAMPLE
  pwsh scripts/campello_rebuild/recipe_walk.ps1                # show current
  ... -Verdict NOT_RECIPE -Locus "-" -Note "section heading"   # verdict+advance
  ... -Status
#>
[CmdletBinding()]
param(
  [ValidateSet('MATCH', 'DEVIATION', 'NOT_RECIPE', 'AMBIGUOUS')]
  [string]$Verdict,
  [string]$Locus = '-',
  [string]$Note = '-',
  [switch]$Status
)

$ErrorActionPreference = 'Stop'
$dir = Join-Path $PSScriptRoot '..\..\outputs\campello_rebuild\recipe_walk'
$dir = (Resolve-Path $dir).Path
$tsv = Join-Path $dir 'recipe_paragraphs.tsv'
$curFile = Join-Path $dir 'cursor.json'
$vFile = Join-Path $dir 'walk_verdicts.tsv'

function Get-Rows {
  $lines = Get-Content -LiteralPath $tsv -Encoding utf8
  $rows = @{}
  foreach ($ln in $lines[1..($lines.Count - 1)]) {
    if ($ln.Trim().Length -eq 0) { continue }
    $p = $ln -split "`t", 5
    $rows[[int]$p[0]] = [pscustomobject]@{
      id = [int]$p[0]; source = $p[1]; page = $p[2]; kind = $p[3]; text = $p[4]
    }
  }
  return $rows
}

function Show-Row($rows, $id, $cur) {
  if ($id -ge $cur.total) {
    Write-Output "WALK COMPLETE  ($($cur.total) paragraphs, all verdicted)."
    return
  }
  $r = $rows[$id]
  Write-Output ("=" * 72)
  Write-Output ("PARAGRAPH {0} / {1}   [source={2} pdf_page={3} kind={4}]" -f `
      $r.id, ($cur.total - 1), $r.source, $r.page, $r.kind)
  Write-Output ("=" * 72)
  Write-Output $r.text
  Write-Output ("-" * 72)
  Write-Output ("verdict it:  recipe_walk.ps1 -Verdict <MATCH|DEVIATION|" +
    "NOT_RECIPE|AMBIGUOUS> -Locus <file:line> -Note <why>")
}

$cur = Get-Content -LiteralPath $curFile -Raw -Encoding utf8 | ConvertFrom-Json
$rows = Get-Rows

if ($Status) {
  $vc = (Get-Content -LiteralPath $vFile -Encoding utf8).Count - 1
  Write-Output ("cursor.current_paragraph_id = {0} / total {1}   |   verdicts written = {2}" -f `
      $cur.current_paragraph_id, $cur.total, $vc)
  return
}

if (-not $Verdict) {
  Show-Row $rows $cur.current_paragraph_id $cur
  return
}

# verdict path: append, advance, show next
$id = [int]$cur.current_paragraph_id
if ($id -ge $cur.total) { Write-Output 'Walk already complete.'; return }
$safeNote = ($Note -replace "`t", ' ') -replace "`r?`n", ' '
$safeLoc = ($Locus -replace "`t", ' ')
Add-Content -LiteralPath $vFile -Encoding utf8 -Value `
  ("{0}`t{1}`t{2}`t{3}" -f $id, $Verdict, $safeLoc, $safeNote)
$cur.current_paragraph_id = $id + 1
($cur | ConvertTo-Json -Compress) | Set-Content -LiteralPath $curFile -Encoding utf8
Write-Output ("verdict[{0}] = {1}  locus={2}  -> advanced to {3}" -f `
    $id, $Verdict, $safeLoc, $cur.current_paragraph_id)
Write-Output ''
Show-Row $rows $cur.current_paragraph_id $cur
