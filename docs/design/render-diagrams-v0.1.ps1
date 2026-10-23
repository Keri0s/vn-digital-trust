param(
    [Parameter(Mandatory=$true)][string]$PlantUmlJar,
    [string]$Java = 'java'
)
$ErrorActionPreference = 'Stop'
$jarPath = (Resolve-Path -LiteralPath $PlantUmlJar).Path
$expected = '5E1ECFA8ECD32C90B03BBF3B1EB6F020943F98AB0FCF4032BE31A0002EE2C462'
if ((Get-FileHash -LiteralPath $jarPath -Algorithm SHA256).Hash -ne $expected) {
    throw 'Requires the pinned PlantUML 1.2026.8 JAR documented in validation-v0.1.md.'
}
$diagramSources = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.puml' -File | Sort-Object Name | Select-Object -ExpandProperty FullName)
if ($diagramSources.Count -lt 4) { throw 'Expected at least three ERD sources and one upload sequence.' }
foreach ($format in @('svg','png')) {
    & $Java '-Djava.awt.headless=true' '-jar' $jarPath '-charset' 'UTF-8' '-failfast2' "-t$format" @diagramSources
    if ($LASTEXITCODE -ne 0) { throw "PlantUML $format render failed." }
}
