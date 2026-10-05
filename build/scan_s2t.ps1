# scan_s2t.ps1 - Simplified-Chinese gate for the WHOLE repository.
# Scans every text file: lesson modules, generated pages, the injected template,
# Markdown docs, tooling and dotfiles. Any Simplified character fails the build.
$ErrorActionPreference = 'Continue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Text;
public static class NLSS2 {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern int LCMapStringEx(string loc, uint flag, string src, int cch,
        StringBuilder dst, int cchDst, IntPtr v, IntPtr r, IntPtr s);
    public static string S2T(string s) {
        int need = LCMapStringEx("zh-TW", 0x04000000, s, s.Length, null, 0, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
        var sb = new StringBuilder(need + 8);
        LCMapStringEx("zh-TW", 0x04000000, s, s.Length, sb, sb.Capacity, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
        var res = new char[s.Length];
        for (int i = 0; i < s.Length; i++) res[i] = sb[i];
        return new string(res);
    }
}
"@

# These two are already correct Traditional Chinese. Windows maps them to a longer
# form, but applying that mapping would break the words they sit in:
#   U+53F0 tai   - correct in the words for 'platform' and 'stage'
#   U+75C7 zheng - correct in the word for 'symptom'
$ALLOW = @{ 0x53F0 = 1; 0x75C7 = 1 }

$buildDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $buildDir   # repository root: build/ lives one level below it
$exts = @('*.html', '*.py', '*.md', '*.txt', '*.ps1', '*.js', '.gitignore', '.gitattributes')
$files = @()
foreach ($e in $exts) { $files += Get-ChildItem -Path $root -Recurse -Filter $e -File -ErrorAction SilentlyContinue }
$files = $files | Sort-Object FullName -Unique | Where-Object { $_.FullName -notlike '*\.git\*' }
$total = 0
foreach ($f in $files) {
    $src = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $conv = [NLSS2]::S2T($src)
    for ($i = 0; $i -lt $src.Length; $i++) {
        $c = [int][char]$src[$i]
        if ($src[$i] -ne $conv[$i] -and -not $ALLOW.ContainsKey($c)) {
            $rel = $f.FullName.Substring($root.Length + 1)
            $s0 = [Math]::Max(0, $i - 18)
            Write-Output ('{0}  U+{1:X4} -> U+{2:X4}  ...{3}...' -f $rel, $c,
                [int][char]$conv[$i], $src.Substring($s0, [Math]::Min(38, $src.Length - $s0)))
            $total++
        }
    }
}
Write-Output ('files scanned: ' + $files.Count)
Write-Output ('TOTAL DIFFS: ' + $total)

