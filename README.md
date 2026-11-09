Nama : Lynorexly Imanuel Tatipikalawan

NPM : 2506546932

Kelas : PBP F

## Tugas6

1. REST adalah arsitektur API berbasis HTTP. JSON saja belum cukup; API juga harus mengikuti prinsip REST, PUT: mengganti seluruh data, dan PATCH: mengubah sebagian daya.

2. Serializers mengubah bentuk MODEL ke JSON serta memvaliadi data masuk, lebih praktis dan terstruktur mengurangi kode manual jika dibandingkan dengan JsonResponse.

3. Autentikasi itu memeriksa identitas pengguna atau user, sedangkan otorisasi memeriksa hak aksesnya. Menyembunyikan tombol di template itu tidak cukup karena pengguna/user bisa mengirim request langsung melalui API atau bahkan browser.

4. CSRF melindungi aplikasi dari request berbahaya yang dikirim dengan  menggunakan sesi login pengguna. force_authenticate() melalui proses autentikasi normal sehingga tidak bisa digunakan karena tidak cukup untuk menguji CSRF. Gunakan APIClient(enforce_csrf_checks=True) serta kirim request tanpa token CSRF, maka pastikan server akan menolaknya.