import { useState } from 'react'
import { A11y, Keyboard, Navigation, Zoom } from 'swiper/modules'
import { Swiper, SwiperSlide } from 'swiper/react'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/zoom'
import { slides } from './slides'
import { useFullscreen } from './useFullscreen'

export default function App() {
  const [activeIndex, setActiveIndex] = useState(0)
  const fullscreen = useFullscreen()

  if (slides.length === 0) return <EmptyState />

  return (
    <main className="slides-viewer relative h-svh">
      <Swiper
        className="h-full"
        modules={[A11y, Keyboard, Navigation, Zoom]}
        keyboard={{ enabled: true }}
        navigation
        zoom={{ maxRatio: 3 }}
        a11y={{
          prevSlideMessage: 'Trang trước',
          nextSlideMessage: 'Trang sau',
          firstSlideMessage: 'Đây là trang đầu',
          lastSlideMessage: 'Đây là trang cuối',
        }}
        onSlideChange={(swiper) => setActiveIndex(swiper.activeIndex)}
      >
        {slides.map((slide, i) => (
          <SwiperSlide key={slide.src} className="px-3 pt-3 pb-16 md:px-20 md:pt-10">
            <div className="swiper-zoom-container">
              <img
                src={slide.src}
                alt={`Trang ${i + 1}`}
                loading={i === 0 ? 'eager' : 'lazy'}
                fetchPriority={i === 0 ? 'high' : 'auto'}
                decoding="async"
              />
            </div>
            {i > 0 && <div className="swiper-lazy-preloader swiper-lazy-preloader-white" />}
          </SwiperSlide>
        ))}
      </Swiper>

      <div className="absolute inset-x-0 bottom-3 z-10 flex items-center justify-center gap-2">
        <span className="rounded-full bg-neutral-900/80 px-3 py-1.5 text-sm tabular-nums text-neutral-300">
          {activeIndex + 1} / {slides.length}
        </span>
        {fullscreen.supported && (
          <button
            type="button"
            onClick={fullscreen.toggle}
            aria-label={fullscreen.isFullscreen ? 'Thoát toàn màn hình' : 'Xem toàn màn hình'}
            title={fullscreen.isFullscreen ? 'Thoát toàn màn hình' : 'Xem toàn màn hình'}
            className="grid size-9 place-items-center rounded-full bg-neutral-900/80 text-neutral-300 transition-colors hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-100"
          >
            <FullscreenIcon exit={fullscreen.isFullscreen} />
          </button>
        )}
      </div>
    </main>
  )
}

function EmptyState() {
  return (
    <main className="grid min-h-svh place-items-center px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold">Chưa có slide nào</h1>
        <p className="mt-3 text-sm leading-6 text-neutral-400">
          Tải slide từ Canva dưới dạng PNG (Share → Download), giải nén rồi bỏ ảnh vào thư mục{' '}
          <code className="rounded bg-neutral-800 px-1.5 py-0.5 text-neutral-200">src/slides/</code>.
          Slide được sắp theo tên file: 1.png, 2.png, …
        </p>
      </div>
    </main>
  )
}

function FullscreenIcon({ exit }: { exit: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className="size-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {exit ? (
        <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
      ) : (
        <path d="M3 8V5a2 2 0 0 1 2-2h3m8 0h3a2 2 0 0 1 2 2v3m0 8v3a2 2 0 0 1-2 2h-3m-8 0H5a2 2 0 0 1-2-2v-3" />
      )}
    </svg>
  )
}
