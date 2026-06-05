param(
    [Parameter(Mandatory = $true)]
    [string]$TunnelUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# Normalize tunnel input / Normaliza a entrada do tunnel
function Get-NormalizedTunnelInfo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RawTunnelUrl
    )

    $value = $RawTunnelUrl.Trim()

    if ($value -notmatch "^https?://") {
        $value = "https://$value"
    }

    $uri = [System.Uri]$value

    return [PSCustomObject]@{
        BaseUrl = $uri.GetLeftPart([System.UriPartial]::Authority)
        Domain = $uri.Host
    }
}

# Check DNS resolution / Verifica a resolução DNS
function Test-DnsResolution {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Domain,

        [string]$Server,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    try {
        $records = if ($Server) {
            Resolve-DnsName $Domain -Server $Server -ErrorAction Stop
        }
        else {
            Resolve-DnsName $Domain -ErrorAction Stop
        }

        $ipv4 = @(
            $records |
                Where-Object { $_.Type -eq "A" -and $_.IPAddress } |
                Select-Object -ExpandProperty IPAddress
        )

        return [PSCustomObject]@{
            Label = $Label
            Ok = $true
            Ipv4 = $ipv4
            Error = $null
        }
    }
    catch {
        return [PSCustomObject]@{
            Label = $Label
            Ok = $false
            Ipv4 = @()
            Error = $_.Exception.Message
        }
    }
}

# Test curl endpoint with default resolver / Testa endpoint curl com resolvedor padrão
function Test-CurlEndpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,

        [string]$ResolveOption,

        [string[]]$ExtraArgs = @()
    )

    $arguments = @("-sS", "-L", "-w", "`nHTTP_STATUS:%{http_code}`n")

    if ($ResolveOption) {
        $arguments += @("--resolve", $ResolveOption)
    }

    $arguments += $ExtraArgs
    $arguments += $Url

    $output = & curl.exe @arguments 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | Out-String).Trim()
    $ok = $exitCode -eq 0 -and $text -match "HTTP_STATUS:(2\d\d|3\d\d)"

    return [PSCustomObject]@{
        Ok = $ok
        ExitCode = $exitCode
        Output = $text
    }
}

# Test assistant search with curl / Testa busca de assistant com curl
function Test-CurlAssistantSearch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl,

        [string]$ResolveOption
    )

    return Test-CurlEndpoint `
        -Url "$BaseUrl/assistants/search" `
        -ResolveOption $ResolveOption `
        -ExtraArgs @("-X", "POST", "-H", "Content-Type: application/json", "-d", "{}")
}

$tunnel = Get-NormalizedTunnelInfo -RawTunnelUrl $TunnelUrl

Write-Host "Sentrya Ops V2 LangGraph tunnel diagnostic"
Write-Host "Base URL: $($tunnel.BaseUrl)"
Write-Host "Domain: $($tunnel.Domain)"

$defaultDns = Test-DnsResolution -Domain $tunnel.Domain -Label "Default DNS"
$cloudflareDns = Test-DnsResolution -Domain $tunnel.Domain -Server "1.1.1.1" -Label "Cloudflare DNS 1.1.1.1"
$googleDns = Test-DnsResolution -Domain $tunnel.Domain -Server "8.8.8.8" -Label "Google DNS 8.8.8.8"

$docsDefault = Test-CurlEndpoint -Url "$($tunnel.BaseUrl)/docs"
$assistantDefault = Test-CurlAssistantSearch -BaseUrl $tunnel.BaseUrl

$publicIpv4 = @($cloudflareDns.Ipv4 + $googleDns.Ipv4 | Where-Object { $_ } | Select-Object -First 1)
$resolveOption = if ($publicIpv4.Count -gt 0) { "$($tunnel.Domain):443:$($publicIpv4[0])" } else { $null }

$docsResolve = $null
$assistantResolve = $null

if (-not $defaultDns.Ok -and ($cloudflareDns.Ok -or $googleDns.Ok) -and $resolveOption) {
    Write-Host ""
    Write-Host "Default DNS failed but public DNS resolved an IPv4 address."
    Write-Host "Running diagnostic-only curl --resolve checks with $resolveOption"
    $docsResolve = Test-CurlEndpoint -Url "$($tunnel.BaseUrl)/docs" -ResolveOption $resolveOption
    $assistantResolve = Test-CurlAssistantSearch -BaseUrl $tunnel.BaseUrl -ResolveOption $resolveOption
}

# Print status line / Imprime linha de status
function Write-StatusLine {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [bool]$Ok
    )

    $status = if ($Ok) { "OK" } else { "FAILED" }
    Write-Host "$Label`: $status"
}

Write-Host ""
Write-Host "Summary"
Write-StatusLine -Label "Default DNS" -Ok $defaultDns.Ok
Write-StatusLine -Label "Cloudflare DNS 1.1.1.1" -Ok $cloudflareDns.Ok
Write-StatusLine -Label "Google DNS 8.8.8.8" -Ok $googleDns.Ok
Write-StatusLine -Label "Docs endpoint with default DNS" -Ok $docsDefault.Ok
Write-StatusLine -Label "Assistant search with default DNS" -Ok $assistantDefault.Ok

if ($docsResolve -ne $null) {
    Write-StatusLine -Label "Optional curl --resolve docs check" -Ok $docsResolve.Ok
}

if ($assistantResolve -ne $null) {
    Write-StatusLine -Label "Optional curl --resolve assistant check" -Ok $assistantResolve.Ok
}

Write-Host ""
Write-Host "Final diagnosis:"

if (-not $defaultDns.Ok -and ($cloudflareDns.Ok -or $googleDns.Ok)) {
    Write-Host "DIAGNOSIS: Public DNS resolves this tunnel domain, but the default Windows DNS resolver does not."
    Write-Host "This is a local Windows/network DNS issue, not a Sentrya Ops code issue."
    Write-Host "curl.exe, Invoke-RestMethod, and the browser/Studio may fail because they usually use the default resolver."
}
elseif (-not $defaultDns.Ok -and -not $cloudflareDns.Ok -and -not $googleDns.Ok) {
    Write-Host "DIAGNOSIS: All DNS checks failed."
    Write-Host "The tunnel may have expired, the terminal running langgraph dev --tunnel may be closed, or Cloudflare has not published this temporary domain."
}
elseif ($defaultDns.Ok -and -not $docsDefault.Ok) {
    Write-Host "DIAGNOSIS: Default DNS resolves, but the tunnel HTTP endpoint failed."
    Write-Host "Check that langgraph dev --tunnel is still running and that the current tunnel URL is correct."
}
else {
    Write-Host "DIAGNOSIS: Default DNS and tunnel checks appear reachable from this terminal."
    Write-Host "If Studio still fails, check browser Allowed Origins, extensions, VPN/proxy, cache, or another browser profile."
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "- Keep the 'langgraph dev --tunnel' terminal open while testing."
Write-Host "- If public DNS resolves but default DNS fails, fix local Windows/network DNS or try another network."
Write-Host "- If Studio blocks the domain, add the generated domain to Allowed Origins."
Write-Host "- If the tunnel domain changes, update Studio base URL and Allowed Origins again."
Write-Host "- curl --resolve is diagnostic-only and does not fix browser/Studio DNS resolution."
