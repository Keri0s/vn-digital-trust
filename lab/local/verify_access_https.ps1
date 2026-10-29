# Read-only checks against the real local deployment. Never bypass TLS validation.
param([string]$OutputPath = '.runtime/checks/access-https-checks.json')
$ErrorActionPreference = 'Stop'
$checks = [System.Collections.Generic.List[object]]::new()
$base = 'https://localhost:8443'
function Record-Check([string]$Name, [bool]$Passed) {
    $checks.Add([pscustomobject]@{check=$Name; passed=$Passed})
}
foreach ($name in @('auth.css','auth.js','admin.css','admin.js')) {
    $response = Invoke-WebRequest "$base/static/vdt/$name" -UseBasicParsing
    Record-Check "HTTPS asset $name is available" ($response.StatusCode -eq 200 -and $response.RawContentLength -gt 0)
}
$homeResponse = Invoke-WebRequest "$base/" -UseBasicParsing
Record-Check 'Home exposes administration navigation and forced-password-change notice' ($homeResponse.Content.Contains('admin-navigation') -and $homeResponse.Content.Contains('temporary-password-notice'))
$redirected = Invoke-WebRequest "$base/admin/users" -UseBasicParsing
Record-Check 'Anonymous administration page redirects to login' ($redirected.Content.Contains('login-form') -and -not $redirected.Content.Contains('admin-content'))
foreach ($path in @('users','roles','permissions','role-assignments','audit-events')) {
    $status = 0
    try { $response = Invoke-WebRequest "$base/api/v1/$path" -UseBasicParsing; $status=[int]$response.StatusCode }
    catch { if ($_.Exception.Response) { $status=[int]$_.Exception.Response.StatusCode } else { throw } }
    Record-Check "Anonymous API $path is denied" ($status -eq 401)
}
$report = [pscustomobject]@{
    recorded_at=[DateTimeOffset]::UtcNow.ToString('o')
    scope='REAL_LOCAL_HTTPS_READ_ONLY_ACCESS_BOUNDARIES'; url=$base
    tls_validation='WINDOWS_TRUST_STORE'; checks=$checks.ToArray()
    passed=@($checks | Where-Object passed).Count
    failed=@($checks | Where-Object { -not $_.passed }).Count
    actual_operator_credentials_used=$false; CRM_FLOW_TC_VALID_G='NOT_RUN'
}
$json=$report | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText((Join-Path (Get-Location) $OutputPath), $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
$json
if ($report.failed -gt 0) { exit 1 }
