$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices; using System.Text;
public static class NLSS {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern int LCMapStringEx(string lpLocaleName, uint dwMapFlags,
        string lpSrcStr, int cchSrc, StringBuilder lpDestStr, int cchDest,
        IntPtr lpVersionInformation, IntPtr lpReserved, IntPtr sortHandle);
    public static string S2T(string s) {
        const uint TRAD = 0x04000000;
        int need = LCMapStringEx("zh-TW", TRAD, s, s.Length, null, 0,
                                 IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
        var sb = new StringBuilder(need + 8);
        LCMapStringEx("zh-TW", TRAD, s, s.Length, sb, sb.Capacity,
                      IntPtr.Zero, IntPtr.Zero, IntPtr.Zero);
        var res = new char[s.Length];
        for (int i = 0; i < s.Length; i++) res[i] = sb[i];
        return new string(res);
    }
}
"@

# Windows maps these characters to a different form even though they are already
# correct Traditional Chinese; converting them would break the words they sit in.
$ALLOW = @{ 0x53F0 = 'correct Traditional: platform / stage'; 0x75C7 = 'correct Traditional: symptom' }

$files = @(Get-ChildItem 'lessons_part*.py') + @(Get-ChildItem '..\docs\*.html')
$total = 0
foreach ($f in $files) {
    $src = [System.IO.File]::ReadAllText($f.FullName, [System.Text.Encoding]::UTF8)
    $conv = [NLSS]::S2T($src)
    for ($i = 0; $i -lt $src.Length; $i++) {
        $c = [int][char]$src[$i]
        if ($src[$i] -ne $conv[$i] -and -not $ALLOW.ContainsKey($c)) {
            $s0 = [Math]::Max(0, $i - 16)
            Write-Output ('{0}  U+{1:X4} -> U+{2:X4}  ...{3}...' -f $f.Name, $c,
                [int][char]$conv[$i], $src.Substring($s0, [Math]::Min(34, $src.Length - $s0)))
            $total++
        }
    }
}
Write-Output ('TOTAL DIFFS: ' + $total)

