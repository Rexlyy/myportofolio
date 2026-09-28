Nama : Lynorexly Imanuel Tatipikalawan

NPM : 2506546932

Kelas : PBP F

## Tugas4

## Features
- Menampilkan halaman utama portfolio
- Menampilkan pengalaman
- Menampilkan daftar skill
- Pencarian skill berdasarkan nama
- Register dan login user
- Logout
- Session authentication
- Last login menggunakan cookie
- Authorization berdasarkan role pengguna
- Role Editor menggunakan Django Group dan Permission
- Create, update, dan delete skill berdasarkan hak akses
- Memberikan dan membatalkan star pada skill
- Menampilkan jumlah star
- Menampilkan status star pengguna
- JSON API untuk data skill
- Perlindungan CSRF pada form POST

## Authorization

Project memiliki empat kondisi akses pengguna:

| Role | Read | Star | Create | Update | Delete |
|------|------|------|--------|--------|--------|
| Pengunjung | ✓ | - | - | - | - |
| User | ✓ | ✓ | - | - | - |
| Editor | ✓ | ✓ | - | ✓ | - |
| Superuser | ✓ | ✓ | ✓ | ✓ | ✓ |

Role Editor dibuat menggunakan Django Group dan Permission.

Editor diberikan permission untuk melihat dan mengubah Skill,
tetapi tidak diberikan permission untuk membuat atau menghapus Skill.

Pengecekan authorization dilakukan di sisi server dan bukan hanya
dengan menyembunyikan tombol pada template.

## AI DISCLOSURE
Penggunaan ai untuk memahami beberapa bagian dalam tugas maupun tutorial seperti beberapa function dan kegunaannya serta pemanggilan, penggunaan ai juga membantu dalam memberikan masukan terhadap beberapa function yang bisa di sederhanakan serta membantu tampilan dalam CSS