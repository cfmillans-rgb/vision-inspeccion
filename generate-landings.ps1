<#
.SYNOPSIS
Generador automático de Landing Pages Hiper-locales para SEO.

.DESCRIPTION
Este script lee el index.html base y genera copias optimizadas para diferentes comunas.
Reemplaza menciones genéricas de "Santiago" por la comuna específica, y actualiza los metadatos (Title, Description, URLs) para acaparar búsquedas locales exactas (Ej: "Video Inspección en Las Condes").

.EXAMPLE
.\generate-landings.ps1
#>

$comunas = @("Las Condes", "Providencia", "Ñuñoa", "Vitacura", "Lo Barnechea", "La Florida", "Maipú", "Santiago Centro", "San Miguel")
$baseFile = "index.html"
$outputDir = "comunas"

if (-Not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

$baseHtml = Get-Content -Path $baseFile -Raw -Encoding UTF8

foreach ($comuna in $comunas) {
    # Formatear el nombre para la URL (ej. "Las Condes" -> "las-condes")
    $slug = $comuna.ToLower().Replace(" ", "-").Replace("ñ", "n")
    $outputFile = Join-Path $outputDir "$slug.html"
    
    Write-Host "Generando Landing B2B/B2C para: $comuna ($slug.html)..."

    # Hacemos una copia del contenido base
    $html = $baseHtml

    # 1. Ajustar rutas relativas (como estamos en un subdirectorio /comunas/, los assets deben apuntar un nivel arriba)
    $html = $html -replace '"\./assets/', '"../assets/'
    $html = $html -replace '"assets/', '"../assets/'
    $html = $html -replace '"\./styles\.css"', '"../styles.css"'
    $html = $html -replace '"\./app\.js"', '"../app.js"'
    $html = $html -replace '"\./blog/', '"../blog/'
    $html = $html -replace '"\./index\.html"', '"../index.html"'
    
    # 2. Modificaciones SEO
    $html = $html -replace '<title>Video Inspección de Tuberías en Santiago', "<title>Video Inspección de Tuberías en $comuna"
    $html = $html -replace 'Video inspección técnica de tuberías y ductos en Santiago', "Video inspección técnica de tuberías y ductos en $comuna"
    $html = $html -replace 'Video Inspección en Santiago', "Video Inspección en $comuna"
    
    # 3. Modificaciones de Copywriting (Hero)
    $html = $html -replace 'Video Inspección de Tuberías en Santiago<br/>', "Video Inspección de Tuberías en $comuna<br/>"
    $html = $html -replace 'quiero agendar una video inspección en Santiago', "quiero agendar una video inspección en $comuna"
    
    # 4. Modificaciones JSON-LD
    $html = $html -replace '"addressLocality": "Santiago"', "`"addressLocality`": `"$comuna`""
    $html = $html -replace '"https://videoinspeccion.cl/"', "`"https://videoinspeccion.cl/comunas/$slug.html`""

    # Escribir el nuevo archivo
    Set-Content -Path $outputFile -Value $html -Encoding UTF8
}

Write-Host "¡Landings generadas exitosamente en la carpeta /comunas/!"
Write-Host "Recuerda añadir estas nuevas URLs al sitemap.xml."
