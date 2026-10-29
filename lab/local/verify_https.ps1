# Read-only HTTP checks. Uses the Windows certificate trust store; never skips TLS validation.
param([string]$OutputPath = '.runtime/checks/https-checks.json')
$ErrorActionPreference = 'Stop'
$results = [System.Collections.Generic.List[object]]::new()
function Record-Check([string]$Name, [bool]$Passed) {
    $results.Add([pscustomobject]@{check=$Name; passed=$Passed})
}
$base = 'https://localhost:8443'
$homeResponse = Invoke-WebRequest "$base/" -UseBasicParsing
Record-Check 'Windows trust validates HTTPS and login page returns 200' ($homeResponse.StatusCode -eq 200 -and $homeResponse.Content.Contains('Đăng nhập'))
Record-Check 'CSP and clickjacking protection present' ($homeResponse.Headers['Content-Security-Policy'] -match "frame-ancestors 'none'" -and $homeResponse.Headers['X-Frame-Options'] -eq 'DENY')
foreach($asset in @('auth.css','auth.js')) {
    $response = Invoke-WebRequest "$base/static/vdt/$asset" -UseBasicParsing
    Record-Check "Static asset $asset returns 200" ($response.StatusCode -eq 200)
}
$csrfResponse = Invoke-WebRequest "$base/api/v1/auth/csrf" -UseBasicParsing -SessionVariable cookieJar
$token = ($csrfResponse.Content | ConvertFrom-Json).csrf_token
Record-Check 'CSRF request passes the real proxy and is never cached' ($csrfResponse.StatusCode -eq 200 -and $token.Length -gt 0 -and $csrfResponse.Headers['Cache-Control'] -eq 'no-store')
Record-Check 'CSRF cookie requires HTTPS' ($csrfResponse.Headers['Set-Cookie'] -match 'Secure')
function Expect-Status([string]$Name, [string]$Path, [int]$Expected, [string]$Method='GET', [hashtable]$Headers=@{}, [string]$Body='') {
    $parameters = @{Uri="$base$Path"; Method=$Method; Headers=$Headers; WebSession=$cookieJar; UseBasicParsing=$true}
    if($Method -eq 'POST') { $parameters.Body=$Body; $parameters.ContentType='application/json' }
    try { $response=Invoke-WebRequest @parameters; $status=[int]$response.StatusCode }
    catch {
        if($_.Exception.Response) { $status=[int]$_.Exception.Response.StatusCode }
        else { throw }
    }
    Record-Check $Name ($status -eq $Expected)
}
Expect-Status 'Anonymous session returns 401' '/api/v1/auth/session' 401
Expect-Status 'Anonymous domain request returns 401' '/api/v1/assessments' 401
Expect-Status 'Login without CSRF returns 403' '/api/v1/auth/session' 403 'POST' @{} '{}'
Expect-Status 'Cross-origin request returns 403' '/api/v1/auth/csrf' 403 'GET' @{Origin='https://outside.invalid'}
Expect-Status 'Closed login payload rejects unknown fields' '/api/v1/auth/session' 422 'POST' @{'X-CSRFToken'=$token;Origin=$base} '{"username":"synthetic-schema-only","password":"invalid-unused-value","extra":true}'
Expect-Status 'Duplicate JSON keys are rejected' '/api/v1/auth/session' 400 'POST' @{'X-CSRFToken'=$token;Origin=$base} '{"username":"a","username":"b","password":"invalid-unused-value"}'
$report = [pscustomobject]@{
    recorded_at=[DateTimeOffset]::UtcNow.ToString('o'); scope='REAL_LOCAL_HTTPS_ANONYMOUS_BOUNDARIES'
    url=$base; tls_validation='WINDOWS_TRUST_STORE'; checks=$results.ToArray()
    passed=@($results | Where-Object passed).Count; failed=@($results | Where-Object { -not $_.passed }).Count
    authenticated_browser_flow='NOT_RUN_BY_THIS_READ_ONLY_SCRIPT'; CRM_FLOW_TC_VALID_G='NOT_RUN'
}
$token=$null
$json=$report | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText((Join-Path (Get-Location) $OutputPath), $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
$json
if($report.failed -gt 0) { exit 1 }
