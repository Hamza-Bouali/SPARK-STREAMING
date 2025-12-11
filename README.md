# 📈 Real-Time Bitcoin Price Prediction System  
# 📈 Gerçek Zamanlı Bitcoin Fiyat Tahmin Sistemi

Bu proje, Apache Kafka, Apache Spark Structured Streaming ve Makine Öğrenmesi kullanarak gerçek zamanlı Bitcoin fiyat tahmini yapmaktadır.  
This project performs real-time Bitcoin price prediction using Apache Kafka, Apache Spark Structured Streaming, and Machine Learning.

---

## 🚀 1. Introduction / Giriş

**TR:**  
Bu proje, Bitcoin fiyatlarını gerçek zamanlı olarak tahmin edebilen uçtan uca bir büyük veri işleme sistemi geliştirmektedir. Sistem, dağıtık mimari üzerinde veri toplama, işleme ve modelleme adımlarını gerçekleştirmektedir.

**EN:**  
This project develops an end-to-end big data processing system capable of predicting Bitcoin prices in real time. The system performs data ingestion, processing, and modeling on a distributed architecture.

**Amaçlar / Objectives:**
- TR: Gerçek zamanlı veri alımı  
  EN: Real-time data ingestion  
- TR: Streaming veri işleme  
  EN: Streaming data processing  
- TR: Veri ön işleme  
  EN: Data preprocessing  
- TR: Makine öğrenmesi modeli eğitimi  
  EN: Machine learning model training  
- TR: Canlı Bitcoin fiyat tahmini  
  EN: Real-time Bitcoin price prediction  

---

## 🏗️ 2. System Architecture / Sistem Mimarisi

<img width="940" height="529" alt="image" src="https://github.com/user-attachments/assets/309d6a94-4ff7-4b9a-8472-319632f8742b" />

**TR:** Sistem aşağıdaki bileşenlerden oluşmaktadır.  
**EN:** The system is composed of the following components:

1. Data Source (Kaggle Dataset)  
2. Kafka Producer  
3. Apache Kafka & Zookeeper (Docker)  
4. Spark Structured Streaming  
5. Data Preprocessing  
6. Machine Learning Model (Spark MLlib)  
7. Prediction & Evaluation  


---

## ⏱️ 3. Timing Chart / Zamanlama Diyagramı

<img width="945" height="531" alt="image" src="https://github.com/user-attachments/assets/75fb5fa6-1b46-498a-b636-57facc619dc4" />

**TR:**  
Bu diyagram, sistem bileşenlerinin birbirleriyle gerçek zamanlı veri akışı içindeki etkileşimini göstermektedir.

**EN:**  
This timing chart illustrates the real-time interaction flow between system components.

**TR – Süreç:**  
- Producer veriyi okur ve Kafka’ya gönderir.  
- Kafka veriyi topic üzerinden dağıtır.  
- Spark Streaming veriyi alır ve işler.  
- Veri temizleme ve özellik çıkarımı yapılır.  
- ML modeli tahmin üretir.  
- RMSE ile performans değerlendirilir.  

**EN – Process:**  
- Producer reads and sends data to Kafka.  
- Kafka distributes data through the topic.  
- Spark Streaming consumes and processes the data.  
- Cleaning and feature extraction applied.  
- ML model produces predictions.  
- RMSE is used for evaluation.  

---

## 📊 4. Data Source (Kaggle) / Veri Kaynağı

**TR:**  
Kullanılan veri seti "Cryptocurrency Price History" (Kaggle) veri setidir.

**EN:**  
The dataset used is the "Cryptocurrency Price History" dataset from Kaggle.

**Sütunlar / Columns:**
- Date  
- Open  
- High  
- Low  
- Close  
- Volume  
- Market Cap  

---

## 📤 5. Kafka Producer

**TR:**  
Kafka Producer Python ile yazılmıştır ve CSV verisini satır bazlı JSON mesajları hâline getirerek Kafka’ya gönderir.

**EN:**  
The Kafka Producer is written in Python and sends CSV rows as JSON messages to Kafka.

**Görevler / Responsibilities:**
- TR: Pandas ile veri okuma  
  EN: Reading data via Pandas  
- TR: JSON mesaj formatı oluşturma  
  EN: Converting rows to JSON  
- TR: `bitcoin_prices` topic'ine gönderme  
  EN: Producing to `bitcoin_prices` topic  
- TR: Gerçek zaman simülasyonu  
  EN: Real-time simulation  

---

## 🐳 6. Apache Kafka & Docker Infrastructure / Docker Tabanlı Kafka Yapısı

**TR:** Kafka ve Zookeeper Docker Compose ile çalıştırılmaktadır.  
**EN:** Kafka and Zookeeper run using Docker Compose.

**TR – Docker avantajları:**  
- Kolay kurulum  
- Taşınabilirlik  
- İzolasyon  
- Ölçeklenebilirlik  

**EN – Docker advantages:**  
- Easy deployment  
- Portability  
- Isolation  
- Scalability  

---

## ⚡ 7. Spark Structured Streaming

**TR:** Spark, Kafka’dan gelen canlı veriyi işlemek için kullanılır.  
**EN:** Spark is used to process live streaming data from Kafka.

**TR – İşlemler:**  
- Kafka’dan veri tüketme  
- JSON parsing  
- DataFrame dönüştürme  
- Ön işleme  
- ML pipeline’a veri aktarma  

**EN – Operations:**  
- Consuming data from Kafka  
- JSON parsing  
- DataFrame conversion  
- Preprocessing  
- Passing data to ML pipeline  

---

## 🧹 8. Data Preprocessing / Veri Ön İşleme

**TR:**  
Model eğitimi için veri temizleme ve dönüştürme adımları uygulanır.

**EN:**  
Data cleaning and transformation steps are applied before model training.

**TR – Uygulanan Adımlar:**  
- Eksik veri temizleme  
- Tip dönüşümü  
- Feature selection  
- Normalizasyon  

**EN – Steps Applied:**  
- Missing value cleaning  
- Type conversion  
- Feature selection  
- Normalization  

---

## 🤖 9. Machine Learning Pipeline / Makine Öğrenmesi Yapısı

**Model:** Linear Regression  
**Features:** Open, High, Low, Volume, Market Cap  
**Label:** Close Price  

**TR:** VectorAssembler kullanılarak özellikler tek vektörde birleştirilmiştir.  
**EN:** Features are combined into a single vector using VectorAssembler.

---

## 🎯 10. Model Evaluation & Prediction / Model Değerlendirme ve Tahmin

**Metrik / Metric:** RMSE (Root Mean Square Error)

**TR:** Sistem gerçek değerlerle tahminleri karşılaştırır.  
**EN:** The system compares actual and predicted values.

> `![Prediction Graph](assets/prediction.png)` (opsiyonel / optional)

---

## 🛠️ 11. Technologies Used / Kullanılan Teknolojiler

| Technology     | Purpose (EN)                         | Kullanım Amacı (TR)                        |
|----------------|---------------------------------------|--------------------------------------------|
| Python         | Data processing, ML, Producer         | Veri işleme, ML, Kafka Producer            |
| Apache Kafka   | Real-time streaming                   | Gerçek zamanlı veri akışı                  |
| Apache Spark   | Streaming + ML                        | Streaming + Makine Öğrenmesi               |
| Spark MLlib    | ML pipeline                           | ML model yapısı                            |
| Docker         | Container deployment                  | Konteyner tabanlı dağıtım                  |
| Kaggle         | Dataset source                        | Veri kaynağı                                |
| Pandas         | CSV reading                           | CSV okuma                                   |
| Kafka UI       | Monitoring Kafka topics               | Kafka topic takibi                          |
| Linux (WSL)    | Development environment               | Geliştirme ortamı                           |

---

## ✅ 12. Conclusion / Sonuç

**TR:**  
Bu proje, gerçek zamanlı büyük veri işleme ve makine öğrenmesi süreçlerini birleştiren uçtan uca bir sistem sunmaktadır. Kafka, Spark ve Docker ile ölçeklenebilir ve güvenilir bir tahmin mimarisi oluşturulmuştur.

**EN:**  
This project presents an end-to-end system that integrates real-time big data processing and machine learning. Using Kafka, Spark, and Docker, a scalable and reliable prediction architecture has been built.

---

