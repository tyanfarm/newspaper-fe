# Trang chính từ bìa "Thắp sáng" — thiết kế

## Mục đích
Web hiện là trình chiếu 7 slide ảnh. Bìa (slide 1) là ảnh dọc nằm giữa, hai bên đen.
Biến bìa thành **trang chính lấp kín màn hình**, 4 thẻ trên bìa là 4 mục; bấm vào thẻ
thì **trang tương ứng (slide 2–5) mở trong popup, nền sau tối + mờ nhẹ**.
Để web giống một trang web thật, không phải một bộ slide.

## Đã chốt với người dùng
- Bố cục **A**: tiêu đề + 4 thẻ (2×2) ở giữa; trời/giấy/sóng trải rộng hai bên.
- Tiêu đề và hải đăng **to hơn** bản Canva; hải đăng **sát mép trái**.
- Bấm thẻ → popup trang tương ứng, nền **blur đen nhẹ**.
- Các phần trên bìa **tách tự động từ WebP trước**; người dùng sẽ thay bằng file gốc Canva sau.
- Mockup tham chiếu: `.superpowers/brainstorm/.../home-layout-a-v6.html` (không commit).

## Quyết định của Claude (người dùng chưa phản đối)
- Thẻ ↔ mục: Lời ngỏ → slide 2, Vùng ký ức → 3, Cùng nhau lớn → 4, Lời tri ân → 5.
- **Bỏ slide 6** (trùng "Cùng nhau lớn") **và 7** (bìa sau gần trống) khỏi web; file gốc giữ ở `design/canva-export/`.
- Popup: đóng bằng X / bấm nền / Esc / nút Back; vuốt hoặc mũi tên để sang mục kế; chạm đúp/pinch để phóng to.
- Mỗi mục có link riêng: `#loi-ngo`, `#vung-ky-uc`, `#cung-nhau-lon`, `#loi-tri-an`. Mở link → vào thẳng popup.
- Điện thoại / màn dọc: thẻ 2×2, hải đăng nằm dưới thẻ (theo mockup khung điện thoại).
- Tiêu đề tab: "Thắp sáng – L2T NEWS".

## Không làm
- Không dựng lại chữ trong thẻ/trang thành HTML (giữ ảnh).
- Không vẽ lại vệt sáng hải đăng, không làm hiệu ứng chuyển động phức tạp.
- Không thêm framework test; kiểm tra bằng lint + build + trình duyệt headless.

## Cách làm

### Asset (`src/assets/cover/`) — mỗi phần một file, tên cố định để thay bằng bản Canva
| File | Nguồn |
|---|---|
| `title.webp` | rembg + lọc alpha (bỏ bóng mờ dòng phụ) |
| `lighthouse.webp`, `ship.webp`, `bird.webp` | rembg (isnet-general-use) |
| `card-loi-ngo.webp` … `card-loi-tri-an.webp` | cắt theo khung viền thư dò tự động; alpha = đặc trong khung + matte rembg ngoài khung (giữ bướm, hoa, ảnh thò ra) |
| `sea-tile.webp` | dải sóng gốc + bản lật gương → lát liền |
| `paper-tile.webp` | mảng giấy sạch giữa 2 thẻ trên, lật gương 2×2 |
| `logos.webp` | cắt chữ nhật, hiển thị trên nền trắng bo góc |

Script tái tạo: `scripts/extract-cover.py` (Python + rembg, chạy tay, không chạy trong CI).
Ảnh các mục: `src/assets/sections/<slug>.webp` (từ slide 2–5).

### Giao diện
- **Home** (`100svh`, không cuộn): nền = gradient màu trời (lấy từ bìa) + `paper-tile` lặp.
  Cột giữa (tiêu đề ảnh + dòng phụ chữ thật "Ấn phẩm của L2T NEWS" + lưới thẻ 2×2) dùng CSS
  layout, kích thước theo `min(vw, vh)` để vừa mọi tỉ lệ màn hình. Trang trí (hải đăng, sóng,
  thuyền, chim, logo) ghim theo mép viewport.
- Màn ngang ↔ màn dọc chuyển bằng `@media (max-aspect-ratio: 1/1)`.
- Thẻ là `<button>` (aria-label = tên mục), hover nhấc nhẹ; tắt khi `prefers-reduced-motion`.
- **SectionDialog**: `<dialog>` + `showModal()` (khóa focus, Esc sẵn có). `::backdrop` =
  `rgb(0 0 0 / .55)` + `backdrop-filter: blur(6px)`. Bên trong: Swiper (Keyboard, Navigation,
  Zoom, A11y) 4 mục, mở đúng mục được bấm; tên mục + "x / 4"; nút X.
- **Hash routing**: mở popup → `history.pushState(#slug)`; `popstate`/load đọc hash để mở/đóng;
  đổi mục trong popup → `replaceState`.

### Kiểm tra
`pnpm lint`, `pnpm build`, và Playwright (Chrome hệ thống, script tạm ngoài repo) ở
1920×1080, 1440×900, 1366×768, 1280×800, 2560×1080, 1024×768, 820×1180, 390×844, 375×667:
không tràn/cuộn trang, thẻ không chồng nhau, bấm từng thẻ mở đúng mục, Esc/X/nền/Back đóng,
deep link mở đúng mục, không lỗi console.

## Để builder tự quyết
Con số kích thước/vị trí cụ thể (chỉnh theo ảnh chụp ở các viewport trên), thời lượng animation,
chất lượng nén WebP.
