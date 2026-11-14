# baotuong-fe

Báo tường "Thắp sáng – L2T NEWS" trên web — Vite + React + TypeScript + Tailwind + Swiper.

Trang chính là bìa báo trải kín màn hình, theo mẫu `design/update-v1/homepage-design.webp`:
máy tính thì tiêu đề + hải đăng bên trái, 4 thẻ bên phải; điện thoại thì tiêu đề, 4 thẻ rồi biển
xếp dọc; máy tính bảng dựng đứng thì đúng như mẫu. Bấm một trong 4 thẻ để mở trang đó trong popup
(nền tối, mờ). Lúc popup mở, một đàn bướm bay ra từ thẻ vừa bấm, các hình trong trang lần lượt
hiện ra từ trên xuống, rồi chữ chạy ra từng dòng (trái → phải, trên → dưới). Trang "Lời tri ân"
có video (Google Drive) hiện trong khung ở dưới, sau khi chữ chạy xong. Mỗi mục có link riêng:
`/#loi-ngo`, `/#vung-ky-uc`, `/#cung-nhau-lon`, `/#loi-tri-an`.

## Chạy local

```bash
pnpm install
pnpm dev
```

## Nội dung nằm ở đâu

| Thư mục | Nội dung |
|---|---|
| `design/canva-export/` | File xuất từ Canva, không đưa thẳng lên web: 4 trang `2.webp`–`5.webp` (và bìa cũ `1.webp`) |
| `design/canva-export/objects-png/` | Từng hình (PNG nền trong suốt) của mỗi trang, xuất riêng từ Canva; `homepage/` là hải đăng, sóng, thuyền, logo…; `effects/` là 2 con bướm |
| `design/update-v1/` | Mẫu trang chính mới `homepage-design.webp`; mỗi thư mục con là các hình của 1 thẻ; các file `BÁO TƯỜNG …png` ở ngoài là mây; `title-header.png` là tiêu đề |
| `design/*/placements/` | Vị trí của từng hình trên slide / mẫu, do `scripts/locate-elements.py` dò ra |
| `src/assets/sections/<mục>/` | Trang trong popup, tách lớp: nền giấy, từng hình, phần còn lại của slide, lớp chữ |
| `src/assets/cover/` | Các phần của trang chính, cắt từ hình gốc Canva theo mẫu mới: tiêu đề, logo, 4 thẻ, mây, hải đăng, vệt sáng, sóng, thuyền, chim |
| `src/sections.ts` | Tên + thứ tự 4 mục, link video của "Lời tri ân" |

**Sửa một trang hoặc đổi hình:** xuất lại slide (WebP) và các hình của nó (PNG) từ Canva vào
`design/canva-export/` (trang chính: `design/update-v1/`), rồi chạy lại các script — xem
[scripts/README.md](scripts/README.md).

**Đổi video "Lời tri ân":** sửa link `video` trong `src/sections.ts` (dạng
`https://drive.google.com/file/d/<ID>/preview`; file Drive phải để "Bất kỳ ai có đường liên kết").

Trong popup: vuốt (mobile), phím ← → hoặc nút mũi tên (desktop) để sang mục khác; chạm đúp / pinch để phóng to;
đóng bằng nút ✕, bấm ra vùng tối, phím Esc hoặc nút Back. Máy bật "giảm chuyển động" thì không có bướm,
các hình, chữ và video hiện ngay.

## Deploy (GitHub Actions → Vercel)

Workflow `.github/workflows/ci-deploy.yml`:

| Sự kiện            | Việc chạy                                  |
| ------------------ | ------------------------------------------ |
| Mở / cập nhật PR   | lint + build → deploy **preview**          |
| Push vào `main`    | lint + build → deploy **production**       |

Vercel tự deploy theo Git đã bị tắt trong `vercel.json` (`git.deploymentEnabled: false`)
để không bị deploy 2 lần — mọi deploy đi qua GitHub Actions.

### Setup lần đầu

```bash
# 1. Tạo project trên Vercel và link với thư mục này
pnpm dlx vercel login
pnpm dlx vercel link          # tạo .vercel/project.json (đã gitignore)

# 2. Lấy orgId + projectId
cat .vercel/project.json

# 3. Tạo token tại https://vercel.com/account/tokens, rồi lưu 3 secret vào GitHub repo
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID
```

Sau đó push lên `main` → site có tại `https://<tên-project>.vercel.app`.
