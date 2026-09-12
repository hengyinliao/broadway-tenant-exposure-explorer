param([ValidateSet('dev','build','test')][string]$Task='dev')
$ErrorActionPreference='Stop';Set-Location (Join-Path $PSScriptRoot 'frontend')
$node=Join-Path $env:LOCALAPPDATA 'codex-node\node.exe';if(!(Test-Path $node)){throw 'Install Node.js 22+'}
$env:Path=(Split-Path $node)+';'+$env:Path;& $node '..\..\MetroVancouverLivingFitExplorer\.tools\package\bin\npm-cli.js' run $Task;exit $LASTEXITCODE
