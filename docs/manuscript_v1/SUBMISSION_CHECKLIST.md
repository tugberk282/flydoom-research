# Submission checklist

> **V2 update — 5 November 2026:** The authoritative claim bundle is `outputs/manuscript-evidence-v2/`. Figures 6–7 and their manifest in `outputs/manuscript-figures-v2/` must accompany the historical V1 figures. Run `python scripts/reproduce_publication_v2.py` before any submission or public package update. V1 alone is no longer claim-complete.

Bu liste, V1 kanıt paketini belirli bir dergiye gönderilecek dosyalara dönüştürmek için kullanılır. Hiçbir madde yeni analiz veya endpoint araması gerektirmez.

## Bilimsel içerik

- [x] Başlık, abstract, introduction, results, discussion, limitations ve methods summary mevcut.
- [x] Her ana iddia `CLAIMS_AND_EVIDENCE.md` içinde kaynak artefakt ve SHA-256 ile eşlenmiş.
- [x] Negatif kapılar, external replication başarısızlığı ve `z = 2.816 < 3` sonucu korunmuş.
- [x] Biyolojik sex/population genellemesi ve connectome üstünlüğü iddiaları açıkça sınırlandırılmış.
- [x] Şekil planı ve legendler, beş frozen figure ile eşleşiyor.

## Dergiye uyarlama

- [ ] Hedef derginin kelime, bölüm, kaynak ve şekil çözünürlüğü kurallarını seç.
- [ ] Dergi şablonuna göre Markdown taslağını DOCX/LaTeX biçimine aktar.
- [ ] Yazar sırası, kurum, ORCID ve sorumlu yazar bilgilerini ekle.
- [ ] Author contributions, competing interests, funding ve acknowledgements beyanlarını ekle.
- [ ] Data/code availability metnini dergi formuna göre kısalt; public release URL'sini koru.
- [ ] Son proofreading: sayı biçimi, birim, italik tür adları, şekil çağrıları ve referans eşleşmesi.

## Gönderim öncesi doğrulama

- [ ] `python scripts/reproduce_publication_v1.py` başarıyla çalışıyor.
- [ ] Evidence ve figure testleri geçiyor.
- [ ] PDF dışa aktarımı sayfa taşması, şekil okunabilirliği ve alt yazı çakışması açısından incelendi.
- [ ] Cover letter yalnızca metodolojik katkıyı ve sınırlı sonucu anlatıyor; yeni bilimsel iddia eklemiyor.
