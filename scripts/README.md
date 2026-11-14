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

# 2. Tách lớp cả 4 trang → src/assets/sections/<mục>/  (thêm tên mục để chỉ làm lại trang đó, vd. loi-tri-an)
.venv-scripts/bin/python scripts/build-section-layers.py
```

- `locate-elements.py` tìm mỗi PNG trên slide (SIFT; hình phẳng/nhỏ như cánh hoa thì khớp mẫu), in ra
  độ khớp của từng hình. Hình không tìm được báo `MISSING` — hình đó vẫn hiện trong trang, chỉ là không có hiệu ứng.
  Hình khó dò có thể đặt tay trong `FALLBACK` (`method='fixed'`).
- `build-section-layers.py` in ra sai số khi ghép lại các lớp so với slide (hiện ~1,5–2,5/255) — ghép trên
  giấy cũ thì trông y hệt slide. Giấy của slide được thay bằng tờ thư airmail gấp nếp
  `design/update-v1/cung_nhau_lon/BÁO TƯỜNG 20.11 (10).png` (`PAPER_FILE`, cắt bớt mép `PAPER_TRIM` để dải
  sọc mảnh như cũ): chỗ nào trên slide là giấy trơn hay sọc cũ thì lớp trên trong suốt, bóng đổ và hình vẽ
  giữ lại; chỗ sọc cũ vẽ đè lên ảnh (ảnh lớp học mờ của "Vùng ký ức") thì lấp lại và vẽ sọc mới đè lên. Đặt `PREVIEW_DIR=<thư mục>` để lưu ảnh từng trang trên giấy mới mà xem bằng mắt.
  Chữ được tách riêng (`text.webp`) cùng toạ độ từng dòng để chạy ra từng dòng; vùng chữ của mỗi trang
  khai báo trong `TEXT_BLOCKS`, theo thứ tự đọc (trang "Cùng nhau lớn": hết cột trái rồi mới sang cột phải).
  Khung video (`VIDEO`, trang "Lời tri ân") được để trống trong các lớp: video nằm dưới hoa lá vẽ đè lên
  khung, và chỉ hiện sau khi chữ chạy xong.

## Trang chính

Theo mẫu `design/update-v1/homepage-design.webp`. Mỗi thư mục con của `design/update-v1/` là các hình của
một thẻ (ghép lại thành `card-<mục>.webp`); các file `BÁO TƯỜNG …png` nằm ngoài là mây; `title-header.png`
là tiêu đề (cả dòng "Ấn phẩm của L2T NEWS"); `click-in-here.png` là dòng hướng dẫn "Chạm vào từng ô để cùng
khám phá!", được cắt đôi ở khoảng trắng sau chữ "ô" (`hint-1`, `hint-2`) để trên màn hình hẹp xuống được 2 dòng.
Hải đăng, vệt sáng, sóng, thuyền, logo lấy từ `design/canva-export/objects-png/homepage/`.

```bash
# 1. Dò vị trí các hình trên mẫu (mỗi thư mục một lần chạy)
for d in design/update-v1 design/update-v1/loi_ngo design/update-v1/vung_ky_uc design/update-v1/cung_nhau_lon \
         design/update-v1/loi_tri_an design/canva-export/objects-png/homepage; do
  .venv-scripts/bin/python scripts/locate-elements.py design/update-v1/homepage-design.webp "$d" \
    "design/update-v1/placements/$(basename "$d").json"
done

# 2. Cắt các phần → src/assets/cover/ + src/coverScene.json
.venv-scripts/bin/python scripts/build-cover-scene.py
```

Mây mờ, không dò được nên đặt tay trong `SLIDE_OVERRIDES` của `locate-elements.py` (cùng với các hình khó
dò khác của mẫu này). `src/coverScene.json` ghi khung của từng phần theo pixel của mẫu; `src/home.css`
thu phóng và neo từng nhóm (tiêu đề + logo, 4 thẻ, biển) theo kích thước màn hình.

`extract-cover.py` là script cũ (tách bìa từ `1.webp`); nền giấy `paper-tile.webp` vẫn là của nó. Đừng chạy
lại: nó ghi đè `title.webp` và `card-*.webp` bằng bản của bìa cũ.
