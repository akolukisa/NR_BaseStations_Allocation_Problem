## Ön Koşullar (macOS)
- Gerekli paketleri kur: `brew install cmake ninja python@3.11 gsl sqlite eigen`
- Python sanal ortam gerekmiyor; NR MIMO özellikleri için `eigen` şarttır.

## Kaynak Kodların Alınması
- ns-3 çekirdeği: `git clone https://gitlab.com/nsnam/ns-3-dev.git`
- NR modülü (5G‑LENA): `git clone https://gitlab.com/cttc-lena/nr.git ns-3-dev/contrib/nr`
- Sürüm uyumluluğu (öneri):
  - NR sürümünü kontrol et: `cd ns-3-dev/contrib/nr && git branch -r | grep 5g-lena`
  - Örn. `git checkout 5g-lena-v2.5.y` ve uygun ns-3 sürümü (ns-3.39) için: `cd ../../ && git checkout ns-3.39`

## Derleme ve Yapılandırma
- Proje kökünde derle: `cd ns-3-dev`
- Yapılandır: `./ns3 configure --enable-examples --enable-tests`
  - Çıktıda `SQLite support: ON` ve `nr` modülünün listelendiğini doğrula.
  - `Eigen3 support: OFF` uyarısı varsa `brew install eigen` ardından configure/build’i tekrarla.
- Derle: `./ns3 build -j 4`

## Çalıştırma ve Doğrulama
- Örnek yardım çıktısı: `./ns3 run cttc-nr-demo -- --help`
- Basit demo: `./ns3 run cttc-nr-demo -- --simTime=1s --gNbNum=3 --ueNumPergNb=10`
- Beamforming/MIMO örnekleri (Eigen gerekir): `./ns3 run cttc-realistic-beamforming -- --help`
- Sık hata nedenleri ve çözüm:
  - Yanlış dizinde çalıştırma: komutlar `ns-3-dev` içinde `./ns3` ile çalıştırılmalı.
  - `Eigen` eksik: NR MIMO özellikleri devre dışı kalır; `brew install eigen` sonrası yeniden configure/build.
  - `ninja: warning: premature end of file`: yeniden `./ns3 build` çalıştır; çoğunlukla geçici.

## Sonuçların Dışa Aktarımı
- NR örneklerinde CSV/SQLite izleri etkin; çıktı dizini `--outputDir` ile ayarlanır.
- İhtiyaç halinde örnekleri modül parametreleriyle KPM/CSI/PRB istatistiklerini dosyaya yazacak şekilde çalıştırıp `results/` altına kopyalayacağız.

## Bizim Simülasyon İskeleti ile Entegrasyon
- Çıktılardan `H[i][j][k]` ve PRB doluluklarını JSON/CSV’ye dönüştür.
- `src/env.py` içine besle ve `src/run_experiments.py` ile GA/HGA/PBIG/Max‑SINR karşılaştırmalarını üret.
- Web arayüzü `http://localhost:8001/web/` sonuçları otomatik okur; sektör tıklamasında metrik özetini gösterir.

## Onay Sonrası Uygulanacak Adımlar
- Sürüm uyumluluğu için NR ve ns‑3 branch checkout’larını uygulayıp yeniden derleyeceğim.
- `cttc-nr-demo` ve bir beamforming örneğini çalıştırıp çıktı dosyalarını `results/` altına yerleştireceğim.
- Gerekirse CSV dönüştürücüyü ekleyip çekirdeğe bağlayacağım ve web arayüzünde güncel metrikleri göstereceğim.