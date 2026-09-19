# Game Design Document (GDD)
## Bakso Bulat Bola Ping Pong

### 1. Deskripsi
**Bakso Bulat Bola Ping Pong** adalah game simulasi manajemen waktu dan memasak dengan grafis 2D *pixel art*. Pemain berperan sebagai pedagang bakso kaki lima yang harus meracik pesanan secara akurat menggunakan mekanika *drag-and-drop* sebelum kesabaran *customer* habis.

---

### 2. Gameplay Utama
* **Tujuan:** Menyiapkan mangkok bakso secara cepat dan akurat sesuai pesanan *customer* untuk mengumpulkan uang dan menjaga reputasi warung.
* **Narasi:** Seorang pemuda baru saja merintis bisnis gerobak baksonya. Dari sekadar menjual bakso urat dan halus, ia harus menghadapi berbagai macam pelanggan dari siang hingga malam untuk membuktikan bahwa baksonya adalah yang terbaik di kota.

---

### 3. Alur Game
Alur dari game adalah sebagai berikut:
1. *Customer* datang dan memberikan pesanan berbentuk tiket yang dapat dilihat oleh pemain.
2. Pemain meracik dan memadukan bahan-bahan sesuai pesanan *customer* ke mangkok utama menggunakan *drag-and-drop*.
3. Pemain menyajikan pesanan yang sudah jadi kepada *customer*.
4. **Sistem Evaluasi:** 
   * Jika pesanan **sesuai**, pemain mendapatkan uang dan reputasi akan naik.
   * Jika pesanan **tidak sesuai**, pemain tidak mendapatkan uang dan reputasi akan turun.
5. Pemain terus melayani *customer* secara beruntun hingga jam operasional harian berakhir.

---

### 4. Mekanika Game
* **Interaksi:** Pemain menekan dan menahan klik kiri pada bahan di etalase/rak, lalu menyeret (*drag*) dan melepaskannya (*drop*) di area *hitbox* mangkok.
* **Variabel Tantangan:** Kecepatan dan jumlah pesanan *customer* dipengaruhi oleh waktu, hari, dan cuaca. Contohnya, jika cuaca hujan, malam hari, dan hari Sabtu, antrean *customer* akan datang lebih padat.

---

### 5. Sistem Skor dan Progress
* **Siklus Hari:** Game berjalan dengan sistem "Hari". Total pendapatan dan reputasi dihitung otomatis saat jam operasional selesai (*autosave*).
* **Ekonomi & Shop:** Uang yang didapatkan dapat digunakan di layar *Shop* sebelum hari berikutnya dimulai untuk membuka bahan-bahan baru.
* **Kompleksitas:** Pesanan *customer* akan menjadi lebih bervariasi dan kompleks seiring bertambahnya jenis bahan yang dimiliki pemain.
* **Kondisi Kalah (Game Over):** Jika reputasi pemain menyentuh angka nol, pemain dinyatakan kalah dan game akan mengulang dari awal.