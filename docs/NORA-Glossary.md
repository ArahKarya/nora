# Glosarium NORA — Network Oracle for Reliable Answers

| | |
|---|---|
| **Dokumen** | Glosarium NORA v1.0 |
| **Produk** | NORA — Network Oracle for Reliable Answers |
| **Kolaborasi** | NOZ × PT Arah Karya Sinergi |
| **Disiapkan oleh** | Tim ArahKarya |
| **Tanggal** | Juni 2026 |
| **Status** | Final |

---

## Pendahuluan

Dokumen ini merupakan glosarium resmi istilah-istilah teknis yang digunakan dalam proyek **NORA (Network Oracle for Reliable Answers)** — platform AI Research Engine berbasis RAG untuk standar telekomunikasi, dikembangkan oleh **NOZ × PT Arah Karya Sinergi**.

Istilah dikelompokkan dalam empat kategori:

- **A** — RAG & AI: konsep dasar sistem retrieval dan kecerdasan buatan yang mendasari NORA.
- **B** — Komponen NORA: komponen arsitektur dan modul internal NORA.
- **C** — Telco / 3GPP: terminologi domain standar telekomunikasi yang menjadi knowledge base NORA.
- **D** — Infrastruktur & Ops: teknologi, alat, dan konfigurasi lingkungan deploy NORA.

Setiap penjelasan ditulis ringkas dan akurat dalam konteks penggunaan NORA. Urutan istilah dalam tiap kategori mengikuti abjad.

---

## A — RAG & AI

| Istilah | Penjelasan |
|---|---|
| **Anti-halusinasi / Grounding** | Prinsip NORA bahwa setiap jawaban *wajib* bersumber dari potongan spec resmi yang diambil via retrieval, bukan dari ingatan parametrik model. Jawaban yang tidak didukung konteks ditolak atau diberi flag LOW CONFIDENCE. |
| **Chunk / Chunking** | Proses memecah dokumen spec panjang menjadi potongan-potongan teks (chunk) yang lebih kecil sebelum diindeks ke vector store. Di NORA, chunking dilakukan berbasis nomor section spec (section-aware chunking), bukan pemotongan ukuran tetap. |
| **Confidence Score** | Nilai numerik 0–1 yang merepresentasikan seberapa yakin NORA terhadap kebenaran suatu jawaban. Dihitung berdasarkan verdict verifier, rata-rata skor similarity chunk terambil, dan ada/tidaknya klaim tanpa dukungan sumber. Nilai < 0,7 memicu flag "LOW CONFIDENCE". |
| **Context Window** | Batas maksimum token yang dapat diproses sekaligus oleh sebuah LLM dalam satu inferensi. Di NORA, konteks diisi dengan chunk hasil retrieval + query user; ukurannya menentukan berapa banyak chunk bisa disertakan sebelum dikirim ke Generator. |
| **Cosine Similarity** | Metrik kemiripan antara dua vektor embedding — dihitung dari kosinus sudut antarkeduanya (rentang 0–1, makin tinggi makin mirip). NORA memakai cosine similarity untuk menentukan chunk mana yang paling relevan terhadap query user saat retrieval. |
| **Dimensi (dim) Embedding** | Jumlah dimensi numerik dalam satu vektor embedding. Semakin tinggi dimensi, semakin banyak informasi semantik yang dapat ditangkap, namun makin besar pula penggunaan memori. Contoh di NORA: Gemini embedding menghasilkan vektor berdimensi 3072, fastembed 384. |
| **Dual-Model** | Arsitektur NORA yang memakai dua model LLM berbeda secara berurutan: Generator (Claude Opus) menghasilkan jawaban awal, lalu Verifier (Claude Sonnet) memeriksa jawaban tersebut terhadap konteks sebelum jawaban dikirimkan ke user. Tujuannya: mengurangi halusinasi via self-validation. |
| **Embedding** | Representasi teks (query atau chunk) sebagai vektor numerik berdimensi tinggi yang menangkap makna semantiknya. Di NORA, embedding digunakan untuk mengubah query user dan isi spec ke dalam ruang vektor yang sama sehingga kemiripan semantik dapat dihitung secara matematis. |
| **Generator** | Peran model LLM pertama dalam pipeline dual-model NORA. Generator (Claude Opus via 9router) menerima prompt yang berisi sistem instruksi, chunk konteks dari hasil retrieval, dan query user, lalu menghasilkan jawaban teknis awal. |
| **Inference** | Proses menjalankan model LLM untuk menghasilkan output (jawaban atau verdict) dari input yang diberikan. Setiap query NORA memerlukan minimal dua inference: satu di Generator dan satu di Verifier. |
| **LLM (Large Language Model)** | Model bahasa besar yang dilatih pada data teks skala masif dan mampu menghasilkan, merangkum, serta menalar teks secara natural. Di NORA, LLM digunakan sebagai Generator (Opus) dan Verifier (Sonnet); LLM tidak menjawab dari ingatan, melainkan dari konteks chunk yang disuplai via RAG. |
| **Loop Verifikasi** | Mekanisme iteratif di NORA Agent Layer: jika Verifier menilai jawaban Generator sebagai INVALID, sistem meregenerasi jawaban dengan prompt termodifikasi (maksimum 2 iterasi ulang). Bertujuan meningkatkan kualitas jawaban secara otomatis tanpa intervensi user. |
| **Prompt Orchestration** | Proses penyusunan dan pengelolaan prompt secara terstruktur oleh NORA Agent Layer, mencakup sistem instruksi, injeksi chunk konteks, dan query user. Prompt Generator dan prompt Verifier dikonstruksi berbeda sesuai perannya. |
| **RAG (Retrieval-Augmented Generation)** | Arsitektur AI yang menggabungkan pencarian (retrieval) dokumen relevan dari knowledge base dengan kemampuan generasi teks LLM. NORA memakai RAG agar jawaban selalu bersumber dari spec resmi (tergrounded), bukan dari memori parametrik model yang rawan halusinasi. |
| **Section-Aware Chunking** | Strategi chunking yang digunakan NORA: dokumen spec dipecah berdasarkan nomor section (mis. `4.7.3 GPRS Attach Procedure`), bukan berdasarkan jumlah kata/token tetap. Menghasilkan chunk yang bermakna secara struktural dan mempermudah pelacakan sumber ke section asli spec. |
| **Top-k Retrieval** | Pengambilan sejumlah k chunk teratas (paling mirip secara semantik) dari vector store sebagai konteks untuk Generator. Di NORA, default k = 5; chunk dipilih berdasarkan cosine similarity tertinggi terhadap embedding query user dalam collection Topik yang aktif. |
| **Vector Store / Vector Database** | Basis data yang dirancang untuk menyimpan dan mencari vektor embedding secara efisien menggunakan operasi kemiripan (similarity search). Di NORA, vector store menyimpan embedding semua chunk spec; query dicocokkan ke sini saat retrieval. Implementasi: ChromaDB (demo) / Qdrant (produksi). |
| **Vektor / Vector** | Array numerik berdimensi tinggi hasil proses embedding yang merepresentasikan makna semantik suatu teks. Dalam konteks NORA, setiap chunk spec dan setiap query user diubah menjadi vektor sehingga perbandingan kemiripan makna dapat dilakukan secara komputasional. |
| **Verifier** | Peran model LLM kedua dalam pipeline dual-model NORA. Verifier (Claude Sonnet via 9router) menerima jawaban Generator beserta chunk konteks, lalu menilai apakah jawaban tersebut didukung penuh oleh konteks. Verdict: VALID / PARTIAL / INVALID. |

---

## B — Komponen NORA

| Istilah | Penjelasan |
|---|---|
| **9router** | Gateway model yang digunakan NORA untuk merutekan permintaan ke model cloud: Claude Opus (Generator), Claude Sonnet (Verifier), dan Gemini embedding. Bertindak sebagai lapisan abstraksi antara NORA Agent Layer dan provider LLM eksternal, sehingga engine bisa diganti via konfigurasi. |
| **ChromaDB** | Vector store embedded yang digunakan NORA pada mode demo/pengembangan (termasuk di RPi5). ChromaDB berjalan dalam proses yang sama dengan backend, ringan di memori, dan cocok untuk volume data medium. Untuk produksi skala besar, ChromaDB dapat digantikan Qdrant tanpa mengubah arsitektur. |
| **Claude Opus (Generator)** | Model `cc/claude-opus-4-8` dari Anthropic, diakses via 9router, berperan sebagai Generator dalam pipeline dual-model NORA. Opus menghasilkan jawaban teknis awal berdasarkan prompt + chunk konteks; dipilih karena kemampuan reasoning mendalam pada domain teknis kompleks seperti spec 3GPP. |
| **Claude Sonnet (Verifier)** | Model `cc/claude-sonnet-4-6` dari Anthropic, diakses via 9router, berperan sebagai Verifier dalam pipeline dual-model NORA. Sonnet memeriksa jawaban Opus terhadap konteks dan mengeluarkan verdict VALID/PARTIAL/INVALID; dipilih karena lebih hemat biaya dari Opus untuk tugas verifikasi. |
| **Collection** | Unit penyimpanan terisolasi dalam ChromaDB (atau Qdrant) yang mengelompokkan semua chunk embedding milik satu Topik. Setiap Topik NORA memiliki collection sendiri (mis. `ts24008` untuk 3GPP TS 24.008) sehingga retrieval tidak bocor lintas-Topik. |
| **fastembed** | Library embedding lokal ringan (Python) yang menghasilkan vektor berdimensi 384. Digunakan NORA sebagai alternatif embedding mode lokal (`NORA_EMBED_BACKEND=local`) ketika 9router tidak tersedia. Tidak membutuhkan GPU, cocok untuk RPi5; trade-off: dimensi lebih rendah dari Gemini. |
| **Gemini Embedding (gemini-embedding-001 dim3072)** | Model embedding dari Google, diakses via 9router, menghasilkan vektor berdimensi 3072. Ini adalah embedding default NORA karena menghasilkan representasi semantik kaya tanpa membebani RAM RPi5 (komputasi di cloud). Model ID: `gemini/gemini-embedding-001`. |
| **Ingest** | Proses memasukkan dokumen spec (file .txt per rilis) ke dalam pipeline NORA: chunking per-section → embedding tiap chunk → penyimpanan ke vector store (ChromaDB) beserta metadata (spec, versi, section). Ingest dilakukan sekali per Topik/rilis; re-ingest dipicu saat ada update spec. |
| **Knowledge Base (KB)** | Kumpulan dokumen spec resmi yang telah diproses dan diindeks untuk satu Topik NORA. Untuk Topik 3GPP TS 24.008, KB terdiri dari 257 rilis versi (.txt hasil konversi dari .doc 3GPP) yang tersimpan di direktori `data/3gpp/24008/txt`. |
| **Multi-Topik** | Kemampuan NORA melayani beberapa knowledge base standar telco yang berbeda secara bersamaan. Setiap Topik memiliki collection dan KB sendiri namun berbagi pipeline RAG yang sama. User memilih Topik sebelum bertanya; admin bisa menambah Topik baru tanpa mengubah kode engine. |
| **NORA Agent Layer** | Inti orkestrasi mandiri NORA — kode Python murni internal NORA (bukan runtime AI generik pihak ketiga) yang menjalankan loop retrieve → generate (Opus) → verify (Sonnet) → validate → loop ulang jika INVALID. Bersifat stateless-per-request, multi-tenant: state (memory, history) disimpan per-user di PostgreSQL, sehingga dapat di-load-balance dan di-scale horizontal. |
| **Ollama** | Runtime model LLM lokal yang memungkinkan NORA beroperasi sepenuhnya tanpa panggilan ke layanan cloud. Digunakan sebagai alternatif swap dari 9router (`NORA_ENGINE=ollama`) untuk mode privacy-first. Model yang didukung: Llama3.1, Qwen, beserta embedding lokal (nomic-embed-text, mxbai-embed-large). |
| **PostgreSQL** | Basis data relasional yang menyimpan seluruh state persisten NORA: data user dan autentikasi, memory percakapan per-user, history query, log interaksi, serta feedback. Penggunaan Postgres memungkinkan NORA Agent Layer tetap stateless-per-request dan aman di-replika. |
| **Query Pipeline** | Rangkaian langkah yang dieksekusi NORA Agent Layer untuk setiap query user: (1) embedding query, (2) retrieval chunk dari collection Topik aktif, (3) konstruksi prompt, (4) generate jawaban (Opus), (5) verify (Sonnet), (6) validasi + hitung confidence, (7) kirim output. |
| **Re-ingest** | Proses menjalankan ulang ingest untuk spec atau rilis yang telah diperbarui. Digunakan saat ada versi spec baru yang perlu diindeks ke ChromaDB. Rilis yang sudah terindeks dapat di-skip (delta ingestion) untuk efisiensi. |
| **Topik** | Unit knowledge base independen dalam NORA, merepresentasikan satu domain/spec standar telco (mis. 3GPP TS 24.008). Setiap Topik memiliki atribut: `id`, `nama`, `deskripsi`, `collection` (ChromaDB), `kb_dir` (lokasi file .txt), dan `status` (live/indexing/planned). Topik pertama yang live: **3GPP TS 24.008**. |

---

## C — Telco / 3GPP

| Istilah | Penjelasan |
|---|---|
| **3GPP (3rd Generation Partnership Project)** | Konsorsium standar internasional yang menghasilkan spesifikasi teknis untuk jaringan telekomunikasi seluler generasi 2G hingga 5G dan seterusnya. NORA menggunakan dokumen spec 3GPP (khususnya seri TS 24.xxx) sebagai sumber knowledge base utamanya. |
| **CC (Call Control)** | Prosedur Layer 3 NAS yang mengelola pembangunan, pengelolaan, dan pemutusan panggilan suara antara Mobile Station dan jaringan core. CC terdefinisi dalam TS 24.008 dan menjadi salah satu domain utama knowledge base NORA Topik #1. |
| **GMM (GPRS Mobility Management)** | Sublayer NAS yang mengelola mobilitas dan registrasi perangkat yang menggunakan layanan data paket GPRS: prosedur Attach, Detach, dan Routing Area Update. GMM tercakup dalam TS 24.008 dan terindeks dalam knowledge base NORA. |
| **GPRS Attach** | Prosedur registrasi yang dilakukan Mobile Station ke jaringan GPRS untuk mengaktifkan layanan data paket, termasuk pertukaran pesan (mis. Attach Request, Attach Accept/Reject) antara MS dan SGSN. Prosedur ini terdefinisi di TS 24.008 §4.7.3 dan merupakan contoh query utama NORA. |
| **Knowledge Base Telco** | Dalam konteks NORA: koleksi dokumen spec telekomunikasi resmi (3GPP, ITU-T, IEEE, GSMA) yang telah diproses, di-chunk, di-embed, dan diindeks ke vector store sebagai sumber jawaban. Setiap knowledge base terikat pada satu Topik. |
| **Layer 3 / L3** | Lapisan ketiga dalam model protokol jaringan — di konteks 3GPP, L3 merujuk pada layer protokol NAS (Non-Access Stratum) antara Mobile Station dan jaringan core, mencakup Mobility Management, Call Control, dan Session Management. TS 24.008 mendefinisikan protokol L3 ini. |
| **MM (Mobility Management)** | Sublayer NAS yang mengelola prosedur mobilitas dan registrasi perangkat 2G/3G di jaringan Circuit-Switched: Location Updating, IMSI Attach/Detach, dan Identification. MM terdefinisi di TS 24.008 dan terindeks dalam knowledge base NORA. |
| **Mobile Radio Interface** | Antarmuka udara antara Mobile Station (handset) dan jaringan akses radio (BTS/NodeB). Istilah ini muncul dalam nama lengkap TS 24.008: *"Mobile radio interface layer 3 specification; Core network protocols"*, menandai scope protokol yang dicakup spec tersebut. |
| **NAS (Non-Access Stratum)** | Lapisan protokol dalam arsitektur 3GPP yang berjalan di atas lapisan akses radio (AS/RAN), menghubungkan Mobile Station langsung ke jaringan core (MSC/SGSN/MME). Protokol NAS mencakup Mobility Management, Session Management, dan Call Control — semuanya terdefinisi di TS 24.008. |
| **Release (R98 – R18)** | Versi tahunan/periodik dari standar 3GPP yang mengelompokkan sekumpulan fitur dan perbaikan. NORA mengindeks 257 rilis TS 24.008 mulai Release 98 (R98, v3.0.0, tahun 1999) hingga Release 18 (R18, seri j, 2026), memungkinkan query berbasis versi spesifik. |
| **Spec / Specification** | Dokumen teknis resmi 3GPP yang mendefinisikan protokol, prosedur, format pesan, dan parameter jaringan telekomunikasi. Spec adalah sumber primer knowledge base NORA; setiap jawaban NORA harus dapat ditelusuri ke section spesifik sebuah spec. |
| **TS 24.008** | Technical Specification 3GPP: *"Mobile radio interface layer 3 specification; Core network protocols; Stage 3"* — mendefinisikan seluruh protokol L3 NAS (MM, GMM, CC, SM) antara MS dan jaringan core. Ini adalah **Topik #1** NORA (reference implementation), dengan 257 rilis yang terindeks. |

---

## D — Infrastruktur & Ops

| Istilah | Penjelasan |
|---|---|
| **bcrypt** | Algoritma hashing password adaptif yang digunakan NORA untuk menyimpan password user secara aman di PostgreSQL. bcrypt secara sengaja lambat (cost factor dapat dikonfigurasi) sehingga tahan terhadap serangan brute-force. |
| **Cloudflare Tunnel** | Layanan tunneling terenkripsi dari Cloudflare yang memungkinkan NORA di RPi5 (jaringan lokal/private) dapat diakses secara aman dari internet tanpa membuka port inbound di firewall. Tidak memerlukan IP publik statik; koneksi keluar dari RPi5 ke Cloudflare edge. |
| **Container** | Unit deployment terisolasi yang mengemas aplikasi beserta dependensinya (kode, runtime, library, konfigurasi). NORA menggunakan container Docker untuk setiap komponen (backend FastAPI, ChromaDB, frontend Next.js) agar dapat di-deploy dan dipindah lintas server secara konsisten. |
| **CORS (Cross-Origin Resource Sharing)** | Mekanisme keamanan browser yang mengontrol permintaan HTTP antara origin yang berbeda (mis. frontend Next.js ke backend FastAPI). NORA mengkonfigurasi CORS agar hanya origin yang diizinkan dapat mengakses API backend. |
| **CSP / HSTS** | **CSP (Content Security Policy)**: header HTTP yang membatasi sumber konten (script, style, gambar) yang boleh dimuat browser, mencegah XSS. **HSTS (HTTP Strict Transport Security)**: header yang memaksa browser selalu menggunakan HTTPS. Keduanya dikonfigurasi di NORA untuk hardening keamanan web. |
| **Dimensi Mismatch** | Error yang terjadi ketika embedding yang tersimpan di vector store memiliki dimensi berbeda dari embedding query yang dikirim saat retrieval (mis. 3072 vs 384). Di NORA, mismatch ini bisa terjadi jika backend embedding diganti tanpa re-ingest ulang seluruh collection. |
| **Docker / Docker Compose** | **Docker**: platform containerisasi yang mengemas aplikasi dan dependensinya dalam container portabel. **Docker Compose**: alat orkestrasi multi-container yang mendefinisikan dan menjalankan seluruh stack NORA (backend + ChromaDB + frontend) via satu file `docker-compose.yml`. |
| **earlyoom** | Daemon Linux yang memonitor penggunaan memori secara aktif dan mematikan proses paling boros RAM sebelum kernel OOM killer beraksi. Diinstal di RPi5 untuk menjaga stabilitas NORA saat menjalankan proses embedding atau LLM lokal (Ollama) yang menekan memori. |
| **httpOnly Cookie** | Cookie dengan flag `HttpOnly` yang tidak dapat diakses JavaScript di browser — hanya dikirim melalui header HTTP. NORA menggunakan httpOnly cookie untuk menyimpan session token/JWT agar terlindungi dari serangan XSS yang mencoba mencuri token autentikasi. |
| **JWT (JSON Web Token)** | Token terenkripsi berbasis standar RFC 7519 yang digunakan NORA untuk autentikasi stateless: setelah login, server menerbitkan JWT yang disimpan di httpOnly cookie; setiap request selanjutnya menyertakan token ini untuk verifikasi identitas user. |
| **mmap** | Mekanisme memory-mapped file di Linux yang memungkinkan file dibaca langsung ke virtual address space proses tanpa menyalin ke heap. Relevan di RPi5 saat ChromaDB atau Ollama memuat file model/index besar: mmap mengurangi penggunaan RAM aktif karena halaman dimuat on-demand. |
| **OOM (Out of Memory)** | Kondisi saat sistem Linux kehabisan RAM yang tersedia dan kernel terpaksa mematikan proses (OOM killer). Di RPi5 8GB, risiko OOM meningkat saat menjalankan Ollama (model lokal besar) bersamaan dengan ChromaDB dan backend. Mitigasi: earlyoom + swap. |
| **PWA (Progressive Web App)** | Teknologi web yang memungkinkan aplikasi NORA diinstall di perangkat user (desktop/mobile) dan bekerja seperti aplikasi native, termasuk dukungan offline terbatas via Service Worker. Frontend Next.js NORA dirancang dengan kapabilitas PWA. |
| **RPi5 (Raspberry Pi 5)** | Single-board computer Raspberry Pi generasi 5 (8GB RAM) yang menjadi target hardware deploy NORA untuk demo dan pengembangan. RPi5 menjalankan seluruh stack NORA via Docker Compose + Cloudflare Tunnel; arsitektur ARM64 dengan keterbatasan memori menjadi pertimbangan desain (pemilihan ChromaDB, Gemini embedding cloud, earlyoom). |
| **Service Worker** | Script JavaScript yang berjalan di background browser, terpisah dari halaman web, dan memungkinkan fitur PWA seperti caching aset dan dukungan offline. Digunakan frontend NORA untuk meningkatkan performa load dan memungkinkan instalasi sebagai PWA. |
| **Swap / Swappiness** | **Swap**: ruang disk yang digunakan kernel Linux sebagai "RAM darurat" ketika RAM fisik penuh — memperlambat sistem tapi mencegah OOM. **Swappiness**: parameter kernel (0–100) yang mengontrol agresivitas penggunaan swap. Di RPi5, swap dikonfigurasi + swappiness diturunkan untuk menyeimbangkan stabilitas dan performa NORA. |
| **venv (Virtual Environment)** | Lingkungan Python terisolasi yang memisahkan dependensi proyek NORA dari paket sistem Python. Digunakan dalam pengembangan dan deployment non-Docker untuk mencegah konflik versi library (mis. FastAPI, ChromaDB, fastembed). |

---

*© 2026 PT Arah Karya Sinergi × NOZ. Seluruh istilah dalam dokumen ini digunakan dalam konteks NORA — Network Oracle for Reliable Answers.*
