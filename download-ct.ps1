$ct_index = Import-Csv CT.csv
foreach ($publication in $ct_index) {
  if ($publication.year -le 1922) {
    Write-Output $publication.bibtexkey
    if ($publication.bibtexkey -eq "King1900CT9") {
      # https://cdli.earth/update-events/132025.
      $publication.number = 9
    }
    Write-Output "Downloading $($publication.bibtexkey) to CT$($publication.number).csv…"
    Invoke-WebRequest "https://cdli.earth/search?publication_bibtexkey=$($publication.bibtexkey)&limit=1000&format=csv" -OutFile "CT$($publication.number).csv"
  }
}