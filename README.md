# baotuong-fe

Trình chiếu slide Canva trên web — Vite + React + TypeScript + Tailwind + Swiper.

## Chạy local

```bash
pnpm install
pnpm dev
```

## Thêm slide

1. Canva → **Share → Download** → chọn **PNG** (tất cả các trang) → tải file zip.
2. Giải nén, bỏ ảnh vào `src/slides/`.
3. Slide được sắp theo tên file (sort số): `1.png`, `2.png`, …, `10.png`.

Hỗ trợ `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`. Nên đổi sang WebP để web nhẹ hơn.

Điều khiển: vuốt (mobile), phím ← → , nút mũi tên (desktop), chạm đúp / pinch để phóng to.

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
