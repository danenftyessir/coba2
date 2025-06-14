# ATS CV Search Application

**Tugas Besar 3 IF2211 Strategi Algoritma**  
Pemanfaatan Pattern Matching untuk Membangun Sistem ATS Berbasis CV Digital

## 📋 Deskripsi

Aplikasi ATS (Applicant Tracking System) untuk mencari dan mencocokkan kata kunci dalam dokumen CV PDF menggunakan algoritma pattern matching: KMP, Boyer-Moore, Aho-Corasick, dan Levenshtein Distance.

## 🔍 Algoritma yang Diimplementasikan

### 1. Knuth-Morris-Pratt (KMP)
- **Kompleksitas**: O(n + m)
- **Keunggulan**: Efisien untuk pattern tunggal, tidak ada backtracking
- **Penggunaan**: Pencarian kata kunci exact matching

### 2. Boyer-Moore (BM)
- **Kompleksitas**: O(nm) worst case, rata-rata lebih cepat
- **Keunggulan**: Sangat efisien untuk pattern panjang
- **Penggunaan**: Pencarian pattern panjang dengan skip optimization

### 3. Aho-Corasick (Bonus)
- **Kompleksitas**: O(n + m + z)
- **Keunggulan**: Multi-pattern matching dalam satu pass
- **Penggunaan**: Pencarian banyak kata kunci sekaligus

### 4. Levenshtein Distance
- **Kompleksitas**: O(n × m)
- **Keunggulan**: Fuzzy matching untuk typo dan variasi
- **Penggunaan**: Fallback ketika exact matching tidak menemukan hasil

## 🛠️ Requirements

- **Docker & Docker Compose** (untuk PostgreSQL database)
- **uv** (Python package manager)
- **Python 3.9+**

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd Tubes3_StimaSukses
```

### 2. Start Database dengan Auto-Setup
```bash
# Start PostgreSQL dengan auto-initialization
docker-compose up -d
# Database schema akan otomatis dibuat dari file database/init/
```

### 3. Setup dan Jalankan Aplikasi
```bash
cd src
uv sync
uv run main.py
```

## 🗄️ Database Management

### Auto-Initialization
Database schema dibuat otomatis saat container start menggunakan:
- `database/init/01_init_schema.sql` - Schema dan table creation
- `database/init/02_init_permissions.sh` - Permissions setup

### Manual Database Operations
```bash
# Cek status database
docker exec tubes3_postgres pg_isready -U postgres

# Akses database langsung
docker exec -it tubes3_postgres psql -U postgres -d kaggle_resumes

# Re-run schema jika diperlukan
docker exec -i tubes3_postgres psql -U postgres -d kaggle_resumes < database/init/01_init_schema.sql

# Setup permissions ulang
docker exec tubes3_postgres bash /docker-entrypoint-initdb.d/02_init_permissions.sh
```

### Database Schema
```sql
-- Table utama untuk CV data
resumes (
    id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(255),        -- kategori CV (ENGINEERING, HR, etc.)
    file_path TEXT,              -- path ke file PDF
    name TEXT,                   -- nama kandidat
    phone VARCHAR(50),           -- nomor telepon
    birthdate DATE,              -- tanggal lahir
    address TEXT,                -- alamat
    created_at TIMESTAMP,        -- waktu dibuat
    updated_at TIMESTAMP         -- waktu update terakhir
)
```

### Sample Data Insert
```bash
# Insert sample data untuk testing
docker exec -i tubes3_postgres psql -U postgres -d kaggle_resumes << 'EOF'
INSERT INTO resumes (id, category, file_path, name, phone, address) VALUES 
('CV001', 'ENGINEERING', 'data/ENGINEERING/engineer_cv_001.pdf', 'John Doe', '+1234567890', '123 Main St'),
('CV002', 'DATA_SCIENCE', 'data/DATA_SCIENCE/datascientist_cv_001.pdf', 'Jane Smith', '+0987654321', '456 Oak Ave'),
('CV003', 'HR', 'data/HR/hr_cv_001.pdf', 'Bob Johnson', '+1122334455', '789 Pine Rd')
ON CONFLICT (id) DO NOTHING;
EOF
```

### Bulk Data Import
```bash
# Jika ada script Python untuk bulk import
cd src
uv run utils/import_cv_data.py

# Atau import dari CSV (jika tersedia)
docker exec -i tubes3_postgres psql -U postgres -d kaggle_resumes -c "\COPY resumes FROM '/path/to/data.csv' WITH CSV HEADER;"
```

## 📁 Struktur Data

Pastikan folder `data/` berisi CV files dengan struktur:
```
data/
├── ACCOUNTANT/
├── ENGINEERING/
├── HR/
├── DATA_SCIENCE/
└── ... (kategori lainnya)
```

## 💻 Cara Penggunaan

1. **Input Keywords**: Masukkan kata kunci dipisah koma (contoh: "Python, SQL, React")
2. **Pilih Algoritma**: KMP, BM, AC, atau Levenshtein
3. **Set Parameters**: Jumlah hasil (1-50) dan threshold fuzzy (50%-100%)
4. **Search**: Klik tombol "🔍 Search CVs"
5. **View Results**: Lihat CV cards dengan opsi Summary dan View CV

## 🔧 Fitur Utama

- **Exact Matching**: KMP, Boyer-Moore, Aho-Corasick
- **Fuzzy Matching**: Levenshtein Distance untuk typo handling
- **PDF Processing**: Ekstraksi teks otomatis dari CV PDF
- **Database Integration**: PostgreSQL untuk menyimpan metadata CV
- **Information Extraction**: Regex untuk extract skills, experience, education
- **Performance Timing**: Monitoring waktu eksekusi algoritma

## 🐳 Docker Management

### Container Operations
```bash
# Start services
docker-compose up -d

# Stop services  
docker-compose down

# View logs
docker-compose logs postgres

# Restart dengan rebuild
docker-compose down && docker-compose up -d --build
```

### Database Backup & Restore
```bash
# Backup database
docker exec tubes3_postgres pg_dump -U postgres kaggle_resumes > backup.sql

# Restore database
docker exec -i tubes3_postgres psql -U postgres -d kaggle_resumes < backup.sql

# Reset database (hapus semua data)
docker exec tubes3_postgres psql -U postgres -d kaggle_resumes -c "TRUNCATE TABLE resumes RESTART IDENTITY CASCADE;"
```

## 🧪 Testing Algorithms

```bash
cd src
uv run algorithm/kmp.py      # Test KMP
uv run algorithm/bm.py       # Test Boyer-Moore
uv run algorithm/aho_corasick.py  # Test Aho-Corasick

# Test database connection
uv run -c "from database.config_simple import DatabaseConfig; print('DB OK' if DatabaseConfig().test_connection() else 'DB FAIL')"
```

## 📊 Performance

| Algorithm | Pattern Length | Best For |
|-----------|----------------|----------|
| KMP | Any | Single pattern, guaranteed O(n+m) |
| Boyer-Moore | Long (>3 chars) | Large texts, can skip characters |
| Aho-Corasick | Multiple | Many patterns simultaneously |
| Levenshtein | Any | Typo tolerance, fuzzy matching |

## 🔧 Troubleshooting

### Database Issues
```bash
# Container not starting
docker-compose down && docker-compose up -d
docker-compose logs postgres

# Database connection refused
docker exec tubes3_postgres pg_isready -U postgres

# Schema not applied
docker exec -i tubes3_postgres psql -U postgres -d kaggle_resumes < database/init/01_init_schema.sql

# Permissions issues
docker exec tubes3_postgres bash /docker-entrypoint-initdb.d/02_init_permissions.sh
```

### Application Issues
```bash
# Dependencies issues
uv sync --reinstall

# Performance issues
# - Reduce CV count in data folder for testing
# - Use higher fuzzy threshold (80%+)
# - Choose appropriate algorithm for pattern length
```

### Verify Setup
```bash
# Check all services
docker ps | grep tubes3

# Check database tables
docker exec tubes3_postgres psql -U postgres -d kaggle_resumes -c "\dt"

# Check sample data
docker exec tubes3_postgres psql -U postgres -d kaggle_resumes -c "SELECT COUNT(*) FROM resumes;"

# Test application connectivity
cd src && uv run -c "from database.repo import ResumeRepository; print(f'Found {len(ResumeRepository().get_all_resumes())} CVs')"
```

## 👥 Authors

**Tim Stima Sukses - IF2211 Strategi Algoritma ITB**

- **[Muhammad Raihaan Perdana]** - NIM: [13523124] - KMP & Database Integration
- **[Danendra Shafi Athallah]** - NIM: [13523136] - Boyer-Moore & UI Development  
- **[Bryan P. Hutagalung]** - NIM: [18222130] - Aho-Corasick & Regex Extraction

## 📝 License

Tugas Besar 3 IF2211 Strategi Algoritma - Institut Teknologi Bandung

---

**Note**: Database schema otomatis dibuat saat `docker-compose up -d`. Pastikan Docker running dan uv terinstall sebelum memulai aplikasi.Expo panel of Naru Jataka. Text ID. K Inside.
