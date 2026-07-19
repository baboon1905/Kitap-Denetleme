Benchmark Runner
================

Bu basit runner `SummaryIR` örnekleri oluşturur, `SurfaceRealizer` ve `QualityGate`'i çalıştırır ve sonuçları `benchmarks/report.csv` olarak yazar.

Çalıştırma
---------

Windows (venv etkin):

```powershell
cd kitap-degerlendirme-app
venv\Scripts\Activate.ps1
python -m benchmarks.run_benchmarks
```

Çıktı
-----

- `benchmarks/report.csv` — benchmark özet raporu.
