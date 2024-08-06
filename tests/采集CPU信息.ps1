while ($true) {
    # 获取当前时间作为记录时间戳
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    # 使用Get-Process获取所有进程的信息
    Get-Process |
    Select-Object Name, CPU, WorkingSet64 |
    Add-Member NoteProperty Timestamp $timestamp -PassThru |
    Export-Csv -Path "C:\resource_usage_log.csv" -Append -NoTypeInformation

    # 添加带有时间戳的分隔符到CSV文件
    New-Object PSObject -Property @{
        Timestamp = $timestamp
        Name = '##########'
        CPU = ''
        WorkingSet64 = ''
    } | Export-Csv -Path "C:\resource_usage_log.csv" -Append -NoTypeInformation

    # 暂停10秒
    Start-Sleep -Seconds 10
}