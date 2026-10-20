[CmdletBinding()]
param(
 [Parameter(Mandatory)][string]$Executable,
 [Parameter(Mandatory)][string]$Denoiser,
 [Parameter(Mandatory)][string]$Encoder,
 [Parameter(Mandatory)][string]$Vae,
 [Parameter(Mandatory)][string]$Prompt,
 [Parameter(Mandatory)][string]$Output,
 [ValidateRange(64,4096)][int]$Width=1024,
 [ValidateRange(64,4096)][int]$Height=1024,
 [int]$Seed=42,
 [string[]]$ExtraArgs=@(),
 [switch]$DryRun
)
$ErrorActionPreference='Stop'
foreach ($component in @($Executable,$Denoiser,$Encoder,$Vae)) {
 if (-not [IO.Path]::IsPathFullyQualified($component)) {throw "Absolute path required: $component"}
 if (-not (Test-Path -LiteralPath $component -PathType Leaf)) {throw "Required component missing: $component"}
}
if (-not [IO.Path]::IsPathFullyQualified($Output)) {throw 'Absolute output path required.'}
if ([IO.Path]::GetExtension($Output) -ne '.png') {throw 'Output must be PNG.'}
if (Test-Path -LiteralPath $Output) {throw 'Output already exists.'}
if (-not (Test-Path -LiteralPath (Split-Path -Parent $Output) -PathType Container)) {throw 'Output directory missing.'}
$generationArgs=@('--diffusion-model',$Denoiser,'--llm',$Encoder,'--vae',$Vae,'-p',$Prompt,'--steps','8','--cfg-scale','1.0','--sampling-method','euler','--sigmas','1.0,0.978453,0.95418,0.926626,0.89508,0.845148,0.704534,0.414568,0.0','-W',[string]$Width,'-H',[string]$Height,'-s',[string]$Seed,'--diffusion-fa','-o',$Output)+$ExtraArgs
if ($DryRun) {
 [pscustomobject]@{Executable=$Executable;Arguments=$generationArgs;InferenceExecuted=$false}|ConvertTo-Json -Depth 3
 return
}
& $Executable @generationArgs
if ($LASTEXITCODE -ne 0) {throw "Inference failed: $LASTEXITCODE"}
if (-not (Test-Path -LiteralPath $Output -PathType Leaf)) {throw 'Output was not created.'}
if ((Get-Item -LiteralPath $Output).Length -eq 0) {throw 'Output is empty.'}
Write-Output $Output
