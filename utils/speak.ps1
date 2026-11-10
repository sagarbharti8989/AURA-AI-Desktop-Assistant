param([string]$text)
Add-Type -AssemblyName System.Speech
try {
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Speak($text)
} catch {
    # Fallback: use SAPI COM object
    $v = New-Object -ComObject SAPI.SpVoice
    [void]$v.Speak($text, 0)
}
