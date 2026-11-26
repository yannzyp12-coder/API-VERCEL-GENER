# FF Guest Account Generator API

Generate akun guest Free Fire (Garena) otomatis.
Deploy ke Vercel + simpan ke Firebase Firestore.

---

## Struktur

```
ff-guest-gen/
├── api/
│   └── index.py          ← Flask app (Vercel entry point)
├── core/
│   ├── crypto.py         ← AES-128-CBC encrypt/decrypt
│   ├── garena.py         ← Garena OAuth API
│   ├── generator.py      ← Pipeline utama
│   ├── ip_pool.py        ← IP spoofer realistis
│   ├── major.py          ← MajorLogin + MajorRegister
│   └── rarity.py         ← Rarity scoring dari JWT
├── db/
│   └── firebase.py       ← Firestore CRUD
├── proto/
│   ├── my_pb2.py         ← Generate dari .proto lo sendiri
│   └── output_pb2.py     ← Generate dari .proto lo sendiri
├── utils/
│   └── random_gen.py     ← Password, nickname, device_id generator
├── .env.local.example
├── .gitignore
├── requirements.txt
└── vercel.json
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Proto files

Lo perlu compile `.proto` sendiri:

```bash
protoc --python_out=proto/ proto/my.proto
protoc --python_out=proto/ proto/output.proto
```

### 3. Firebase

- Buat project di [Firebase Console](https://console.firebase.google.com)
- Aktifkan Firestore Database
- Download Service Account JSON dari Project Settings → Service Accounts
- Rename jadi `firebase_sa.json` (dev) atau set env `FIREBASE_SA`

### 4. Env local

```bash
cp .env.local.example .env.local
# Edit .env.local isi FIREBASE_SA, RELEASE_VERSION, GAME_VERSION
```

---

## Deploy Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Set secret Firebase
vercel secrets add firebase_sa "$(cat firebase_sa.json)"

# Deploy
vercel --prod
```

---

## Endpoints

| Method | Path | Deskripsi |
|--------|------|-----------|
| POST | `/generate` | Buat akun guest baru |
| GET | `/accounts` | List akun dari Firebase |
| GET | `/accounts/:id` | Get satu akun |
| DELETE | `/accounts/:id` | Hapus akun |
| GET | `/health` | Health check |

### POST `/generate`

**Params (body JSON atau query string):**

| Param | Type | Default | Keterangan |
|-------|------|---------|------------|
| count | int | 1 | Jumlah akun, max 10 |
| region | str | ID | Region server |
| save | bool | true | Simpan ke Firebase |
| name_prefix | str | "" | Prefix nickname |

**Response:**
```json
{
  "accounts": [
    {
      "access_token":  "9f584bd...",
      "account_id":    "19247081518",
      "created_at":    "2026-11-25T05:38:51.082522+00:00",
      "is_ghost":      false,
      "is_unik":       false,
      "jwt_token":     "eyJhbGci...",
      "name":          "rYLTHvzP",
      "open_id":       "489bc96f...",
      "password":      "Dbeckkz1a_733e5b9363d772a61045fb2e10f87d7a",
      "rarity":        "COMMON",
      "rarity_reason": "Score:0",
      "rarity_score":  0,
      "region":        "ID",
      "status":        "success",
      "uid":           "8498072577",
      "unik_label":    ""
    }
  ],
  "cache_fresh":     1,
  "cache_hit":       false,
  "cache_used":      0,
  "elapsed_sec":     0.74,
  "ghost":           false,
  "region":          "ID",
  "release_version": "OB55",
  "success":         true,
  "total_created":   1,
  "total_requested": 1
}
```

---

## Password Format

```
Dbeckkz1a_{md5(uid + timestamp + random)}
Contoh: Dbeckkz1a_733e5b9363d772a61045fb2e10f87d7a
```

## Nickname Format

8 karakter alphanumeric random (A-Z, a-z, 0-9).
Bisa dikustom via `name_prefix` param.

---

## Notes

- Proto files (`my_pb2.py`, `output_pb2.py`) **tidak disertakan** — lo harus compile dari `.proto` lo sendiri
- `firebase_sa.json` **jangan di-commit** ke git
- MajorLogin mencoba platform 1-9 otomatis sampai dapat JWT
