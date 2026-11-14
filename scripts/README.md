# scripts

## extract-cover.py

Tách các phần trên bìa (`design/canva-export/1.webp`) thành ảnh riêng trong `src/assets/cover/`.
Chỉ chạy tay khi bìa thay đổi — không chạy trong CI.

```bash
python3 -m venv .venv-scripts
.venv-scripts/bin/pip install "rembg[cpu]"
.venv-scripts/bin/python scripts/extract-cover.py design/canva-export/1.webp src/assets/cover --sheet /tmp/cover-sheet.png
```

Lần chạy đầu tải model `isnet-general-use` (~180 MB). `--sheet` xuất một ảnh xem trước để kiểm tra mép.

### Thay bằng file gốc từ Canva

Mỗi phần là một file tên cố định. Muốn dùng bản sạch từ Canva thì tải phần đó về (PNG nền trong suốt),
đổi sang WebP và **ghi đè đúng tên file** — không cần sửa code:

| File | Phần trên bìa |
|---|---|
| `title.webp` | Chữ "Thắp sáng – Số 2011" |
| `lighthouse.webp` | Ngọn hải đăng |
| `ship.webp` | Con thuyền |
| `bird.webp` | Một con chim (dùng lặp lại) |
| `card-loi-ngo.webp`, `card-vung-ky-uc.webp`, `card-cung-nhau-lon.webp`, `card-loi-tri-an.webp` | 4 thẻ |
| `logos.webp` | Logo KDI + KDC |
| `sea-tile.webp` | Dải sóng, lặp ngang dọc đáy trang |
| `paper-tile.webp` | Nền giấy, lặp phủ cả trang |

Lưu ý: ghi đè xong mà chạy lại script thì file của bạn sẽ bị ghi đè ngược lại.
