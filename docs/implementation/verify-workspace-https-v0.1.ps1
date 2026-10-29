$ErrorActionPreference = 'Stop'
$checks = [System.Collections.Generic.List[object]]::new()
foreach($name in @('workspace.js','workspace.css','assessments.js','assessments.css')) {
    $response = Invoke-WebRequest -Uri "https://localhost:8443/static/vdt/$name" -UseBasicParsing -TimeoutSec 20
    $source = [IO.File]::ReadAllText((Join-Path (Get-Location) "backend/vdt/static/vdt/$name"))
    $served = [Text.Encoding]::UTF8.GetString($response.RawContentStream.ToArray())
    $checks.Add([pscustomobject]@{check="Deployed asset matches tested source: $name";passed=($response.StatusCode -eq 200 -and $served -eq $source)})
}
foreach($path in @('workspace/setup','systems','assets','data-assets','scenarios','assessments/00000000-0000-4000-8000-000000000001/dossier')) {
    try { $response=Invoke-WebRequest -Uri "https://localhost:8443/api/v1/$path" -UseBasicParsing -TimeoutSec 20; $status=[int]$response.StatusCode }
    catch { if($_.Exception.Response) { $status=[int]$_.Exception.Response.StatusCode } else {throw} }
    $checks.Add([pscustomobject]@{check="Anonymous workspace request denied: $path";passed=($status -eq 401)})
}
$response=Invoke-WebRequest -Uri 'https://localhost:8443/workspace' -UseBasicParsing -TimeoutSec 20
$checks.Add([pscustomobject]@{check='Anonymous workspace page redirects to login';passed=($response.StatusCode -eq 200 -and $response.Content.Contains('id="login-view"'))})
$report=[pscustomobject]@{recorded_at=[DateTimeOffset]::UtcNow.ToString('o');scope='DEPLOYED_WORKSPACE_HTTPS_ANONYMOUS_AND_ASSET_MATCH';tls_validation='WINDOWS_TRUST_STORE';checks=$checks;passed=@($checks | Where-Object passed).Count;failed=@($checks | Where-Object {-not $_.passed}).Count}
$serialized=$report | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText((Join-Path (Get-Location) '.runtime/checks/workspace-https-checks.json'),$serialized,[Text.UTF8Encoding]::new($false))
$serialized
if($report.failed -gt 0) {exit 1}
