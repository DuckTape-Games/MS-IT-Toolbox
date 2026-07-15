<#
Runs a Microsoft Defender quick scan and returns JSON results
#>

##################
### Scan Setup ###
##################

$ErrorActionPreference = "Stop"
$scanType = "Quick Scan"
$scanPathValue = ""
$scanStart = Get-Date

################################
### Validates Defender Status ###
################################

$statusBefore = Get-MpComputerStatus

if (-not $statusBefore.AMServiceEnabled) {
    throw "Microsoft Defender Antivirus service is not enabled."
}

if (-not $statusBefore.AntivirusEnabled) {
    throw "Microsoft Defender Antivirus is not enabled."
}

############################
### Runs the Quick Scan   ###
############################

Start-MpScan -ScanType QuickScan

$statusAfter = Get-MpComputerStatus

$detections = @(
    Get-MpThreatDetection |
    Where-Object {
        $_.InitialDetectionTime -ge $scanStart
    } |
    ForEach-Object {
        $detection = $_
        $threat = Get-MpThreat -ThreatID $detection.ThreatID |
            Select-Object -First 1

        [PSCustomObject]@{
            ThreatID = $detection.ThreatID
            ThreatName = $threat.ThreatName
            SeverityID = $threat.SeverityID
            CategoryID = $threat.CategoryID
            IsActive = $threat.IsActive
            DidThreatExecute = $threat.DidThreatExecute
            InitialDetectionTime = $detection.InitialDetectionTime
            LastThreatStatusChangeTime = $detection.LastThreatStatusChangeTime
            Resources = @($detection.Resources)
        }
    }
)

$result = [PSCustomObject]@{
    ScanType = $scanType
    ScanPath = $scanPathValue
    ScanStartTime = $scanStart
    ScanEndTime = Get-Date
    AntivirusEnabled = $statusAfter.AntivirusEnabled
    RealTimeProtectionEnabled = $statusAfter.RealTimeProtectionEnabled
    QuickScanStartTime = $statusAfter.QuickScanStartTime
    QuickScanEndTime = $statusAfter.QuickScanEndTime
    QuickScanAge = $statusAfter.QuickScanAge
    Detections = $detections
}

$result | ConvertTo-Json -Depth 8 -Compress
