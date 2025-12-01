# NewGeneration_BS_Allocation_Problem

- Amaç: 5G-LENA (ns-3 NR) üzerinde (BS, Beam) atama optimizasyonunu simüle etmek ve GA/HGA/PBIG algoritmalarını karşılaştırmak.

## Ön Hazırlık

- Gerekli araçlar: `git`, `cmake`, `gcc`, `python3`
- macOS için paketler: `brew install cmake ninja python@3.11 gsl` 
- Python bağımlılığı yok, standart kütüphane kullanılır.

## ns-3 ve 5G-LENA Kurulumu

- Kaynak: https://gitlab.com/nsnam/ns-3-dev
- Adımlar:
- `git clone https://gitlab.com/nsnam/ns-3-dev.git`
- `cd ns-3-dev`
- `./ns3 configure --enable-examples --enable-tests`
- `./ns3 build`
- NR modülü dahil edilir; 5G-LENA örnekleri `src/nr` içindedir.

### Sürüm ve Python Notları (macOS)
- Python 3.14 ile bazı ns-3 komut argümanları uyumsuz olabilir. `python3.11 ./ns3 ...` kullan.
- İsteğe bağlı uyumluluk: `contrib/nr` için `5g-lena-v2.5.y` ve ns-3 için `ns-3.39` branch’leri; macOS’ta master ile derleme genellikle daha sorunsuz.

### Örnek Çalıştırma ve Çıktı Alma
- Demo: `python3.11 ./ns3 run cttc-nr-demo -- --simTime=1s --gNbNum=3 --ueNumPergNb=10`
- Çıktıyı dosyaya yazma: `python3.11 ./ns3 run cttc-nr-demo -- --simTime=1s > ../results/nr_demo/output.txt`
- Beamforming yardım: `python3.11 ./ns3 run cttc-realistic-beamforming -- --help`
- Beamforming varsayılan DB: `realistic-beamforming.db` oluşursa `results/nr_beam/` içine taşı.

## Örnek Senaryo Çalıştırma

- `./ns3 run nr-wifi-simple` veya `./ns3 run nr-spectrum-simulation`
- Bu depo `src/run_experiments.py` ile kendi parametreli çalıştırmaları sağlar.
- ns-3 senaryolarını harici çalıştırıp KPM/CSI çıktıları JSON veya CSV olarak bu depoya aktarabilirsiniz.

## Bu Depoda Simülasyon Akışı

- `configs/simulation.json` senaryo parametrelerini tanımlar.
- `src/env.py` çevre ve kanal kazanç üretimini yapar.
- `src/model.py` SINR, throughput, adalet ve amaç fonksiyonunu hesaplar.
- `src/algorithms/` GA, HGA, PBIG ve baseline yöntemlerini içerir.
- `src/run_experiments.py` parametre süpürmesi ve çıktı üretir.

## Çalıştırma

- `python3 src/run_experiments.py --config configs/simulation.json --method ga` 
- `--method` seçenekleri: `ga`, `hga`, `pbig`, `max_sinr`, `random`

## Çıktılar

- Konsolda toplam verim, Jain indeksi, kullanıcı başına hız ve kısıt uygunluğu raporlanır.
- İstenirse CSV çıktı için `--out results.csv` kullanılabilir.

## O-RAN Entegrasyonu Taslağı

- rApp parametreleri: `alpha`, QoS `r_min`, beam kapasite ve güç profilleri.
- xApp karar çıktısı: kullanıcı→(BS, Beam) ataması JSON.
- E2 KPM girdileri JSON/CSV olarak `src/env.py` kanal matrisi H[i][j][k] ve PRB doluluklarına dönüştürülür.

## Notlar

- Yerleşik kanal modeli basitleştirilmiştir; ns-3 çıktıları ile değiştirmeye uygundur.
- Güç tahsisi sabit, atama optimizasyonu odaklıdır.
- Tüm kodda yorum bulunmaz; açıklamalar bu dosyadadır.
