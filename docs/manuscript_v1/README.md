# Manuscript package V1

> **4 November 2026 update:** V1 is preserved as the historical frozen package. Its FAFB-source-dependent interpretation is superseded by [ADDENDUM_2026-11-04.md](ADDENDUM_2026-11-04.md) and the versioned `outputs/manuscript-evidence-v2/` bundle. Do not use the V1 threshold-5 reciprocity candidate or Real-wiring wording without the addendum.

Bu klasör, projenin mevcut BM mekanizma ve external-validation hattını yayıma hazırlanabilir fakat henüz gönderime hazır olmayan bir bilimsel metin paketinde toplar.

## Yetkili içerik

- [MANUSCRIPT_DRAFT.md](MANUSCRIPT_DRAFT.md): ana makale taslağı.
- [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md): hangi cümlenin hangi kanıtla desteklendiği ve hangi iddiaların yasak olduğu.
- [EXPERIMENT_CHRONOLOGY.md](EXPERIMENT_CHRONOLOGY.md): deneylerin ve karar kapılarının sırası.
- [EXTERNAL_VALIDATION_PROTOCOL.md](EXTERNAL_VALIDATION_PROTOCOL.md): yeni specimen gelirse değişmeden uygulanacak doğrulama protokolü.
- [REFERENCES.md](REFERENCES.md): temel veri ve yöntem kaynakları.
- [FIGURE_PLAN.md](FIGURE_PLAN.md): dondurulmuş şekil kapsamı ve yorum sınırları.
- [FIGURE_LEGENDS.md](FIGURE_LEGENDS.md): makale için şekil açıklamaları.

Makine-okunur kanıt paketi:

- `configs/manuscript_evidence_v1.json`
- `outputs/manuscript-evidence-v1/manifest.json`
- `outputs/manuscript-evidence-v1/verification.json`

Şekil paketi:

- `configs/manuscript_figures_v1.json`
- `outputs/manuscript-figures-v1/manifest.json`
- `outputs/manuscript-figures-v1/figure-*.{png,svg,pdf}`

## Güncel durum

Makale sınıflandırması: **metodolojik/karma sonuç çalışması**. Mevcut kanıt bir sex farkı, population genellemesi, biological memory veya behavioral superiority göstermez. Ana development mekanizması tek MaleCNS graphında güçlüdür fakat external testte genellenmemiş ve cross-dataset pipeline ölçeğiyle karışmıştır.

## Yeniden üretim

```powershell
.venv\Scripts\python.exe scripts\build_manuscript_evidence_v1.py
.venv\Scripts\python.exe -m pytest tests\test_manuscript_evidence_v1.py -q
.venv\Scripts\python.exe scripts\build_manuscript_figures_v1.py
.venv\Scripts\python.exe -m pytest tests\test_manuscript_figures_v1.py -q
```

Gönderim öncesi editoryal ve teknik maddeler için [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) dosyasını kullan.

İki komut kanıt dosyalarını değiştirmez; karar pointer'larını ve SHA-256 manifestini yeniden doğrular.

