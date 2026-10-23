param(
    [Parameter(Mandatory = $true)][string]$PlantUmlJar,
    [string]$Java = 'java'
)
$ErrorActionPreference = 'Stop'
$jarPath = (Resolve-Path -LiteralPath $PlantUmlJar).Path
$expectedHash = '5E1ECFA8ECD32C90B03BBF3B1EB6F020943F98AB0FCF4032BE31A0002EE2C462'
if ((Get-FileHash -LiteralPath $jarPath -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'Use the pinned PlantUML 1.2026.8 JAR recorded in diagram-validation-v0.2-r1.md.'
}
$sources = @(
    (Join-Path $PSScriptRoot 'assessment-flow-v0.2.puml'),
    (Join-Path $PSScriptRoot 'retest-sequence-v0.2.puml')
)
foreach ($format in @('svg', 'png')) {
    & $Java '-Djava.awt.headless=true' '-jar' $jarPath '-charset' 'UTF-8' '-failfast2' "-t$format" @sources
    if ($LASTEXITCODE -ne 0) { throw "PlantUML $format rendering failed." }
}
