# baotuong-fe

Báo tường "Thắp sáng – L2T NEWS" trên web — Vite + React + TypeScript + Tailwind + Swiper.

Trang chính là bìa báo trải kín màn hình; bấm một trong 4 thẻ để mở trang đó trong popup
(nền tối, mờ). Mỗi mục có link riêng: `/#loi-ngo`, `/#vung-ky-uc`, `/#cung-nhau-lon`, `/#loi-tri-an`.

## Chạy local

```bash
pnpm install
pnpm dev
```

## Nội dung nằm ở đâu

| Thư mục | Nội dung |
|---|---|
| `src/assets/sections/` | 4 trang mở trong popup: `loi-ngo.webp`, `vung-ky-uc.webp`, `cung-nhau-lon.webp`, `loi-tri-an.webp` |
| `src/assets/cover/` | Các phần của bìa (tiêu đề, hải đăng, thuyền, 4 thẻ, sóng, nền giấy, logo…) |
| `design/canva-export/` | File xuất gốc từ Canva (bìa = `1.webp`), không đưa lên web |
| `src/sections.ts` | Tên + thứ tự 4 mục |

**Sửa một trang:** xuất lại trang đó từ Canva, đổi sang WebP, ghi đè đúng tên file trong `src/assets/sections/`.

**Thay phần trên bìa bằng bản gốc từ Canva** (sạch hơn bản tách tự động): xem
[scripts/README.md](scripts/README.md) — ghi đè đúng tên file trong `src/assets/cover/`, không cần sửa code.
Script `scripts/extract-cover.py` tách lại toàn bộ từ `design/canva-export/1.webp` nếu bìa thay đổi.

Trong popup: vuốt (mobile), phím ← → hoặc nút mũi tên (desktop) để sang mục khác; chạm đúp / pinch để phóng to;
đóng bằng nút ✕, bấm ra vùng tối, phím Esc hoặc nút Back.

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
