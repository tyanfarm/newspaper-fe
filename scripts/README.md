# scripts

Chạy tay khi nội dung thay đổi — không chạy trong CI. Kết quả (ảnh trong `src/assets/`, file JSON) được commit.

```bash
python3 -m venv .venv-scripts
.venv-scripts/bin/pip install opencv-python-headless pillow numpy "rembg[cpu]"
```

## Các trang trong popup (từng hình hiện dần)

Mỗi trang được dựng lại thành nhiều lớp để các hình có thể hiện ra lần lượt mà vẫn **đúng vị trí và thứ tự
chồng như slide gốc**.

```bash
# 1. Dò vị trí từng hình trên slide (mỗi trang một lần chạy; --debug vẽ khung các hình tìm được)
.venv-scripts/bin/python scripts/locate-elements.py design/canva-export/2.webp design/canva-export/objects-png/loi_ngo design/canva-export/placements/loi_ngo.json --debug /tmp/loi_ngo.png
#    tương tự: 3.webp → vung_ky_uc, 4.webp → cung_nhau_lon, 5.webp → loi_tri_an, 1.webp → homepage

# 2. Tách lớp cả 4 trang → src/assets/sections/<mục>/
.venv-scripts/bin/python scripts/build-section-layers.py
```

- `locate-elements.py` tìm mỗi PNG trên slide (SIFT; hình phẳng/nhỏ như cánh hoa thì khớp mẫu), in ra
  độ khớp của từng hình. Hình không tìm được báo `MISSING` — hình đó vẫn hiện trong trang, chỉ là không có hiệu ứng.
  Hình khó dò có thể đặt tay trong `FALLBACK` (`method='fixed'`).
- `build-section-layers.py` in ra sai số khi ghép lại các lớp so với slide (hiện ~1–2/255) — ghép xong trông
  y hệt slide.

## Bìa (trang chính)

```bash
# Hải đăng, vệt sáng, sóng, thuyền, logo, chim, bướm — từ hình gốc Canva, giữ bố cục slide 1
.venv-scripts/bin/python scripts/build-cover-scene.py

# Tiêu đề, 4 thẻ, nền giấy — chưa có bản gốc, tách tự động từ 1.webp (lần đầu tải model ~180 MB)
.venv-scripts/bin/python scripts/extract-cover.py design/canva-export/1.webp src/assets/cover --sheet /tmp/cover-sheet.png
```

`build-cover-scene.py` ghi `src/coverScene.json`: vị trí từng phần theo pixel của slide 1. Trang chủ đặt
chúng theo đúng toạ độ đó (thu phóng theo màn hình), nên hải đăng – vệt sáng – sóng – thuyền – logo giữ
nguyên cách sắp xếp như slide; màn hình rộng thì sóng kéo dài thêm sang phải.

Có bản gốc cho tiêu đề / thẻ / nền giấy thì đổi sang WebP và ghi đè đúng tên file trong `src/assets/cover/`
(`title.webp`, `card-<mục>.webp`, `paper-tile.webp`) — không cần sửa code. Chạy lại `extract-cover.py`
sẽ ghi đè ngược lại các file đó.
