import { useEffect, useRef, type MouseEvent, type SyntheticEvent } from 'react'
import type { Swiper as SwiperInstance } from 'swiper'
import { A11y, Keyboard, Navigation, Zoom } from 'swiper/modules'
import { Swiper, SwiperSlide } from 'swiper/react'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/zoom'
import ButterflyBurst, { type Burst } from './ButterflyBurst'
import './section-dialog.css'
import SectionPage from './SectionPage'
import { sections } from './sections'

type SectionDialogProps = {
  /** Section to show, or null when the popup is closed. */
  index: number | null
  onClose: () => void
  onChange: (index: number) => void
  /** Butterflies to release as the popup opens. */
  burst: Burst | null
}

// Clicks on these keep the popup open; anywhere else (the dark area) closes it.
const KEEP_OPEN = '.section-page, button, .section-dialog__label, .swiper-button-prev, .swiper-button-next'

export default function SectionDialog({ index, onClose, onChange, burst }: SectionDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const swiperRef = useRef<SwiperInstance | null>(null)
  const shown = index ?? 0

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (index === null) {
      if (dialog.open) dialog.close()
      return
    }
    if (!dialog.open) dialog.showModal()
    const swiper = swiperRef.current
    if (swiper) {
      // Swiper measured 0×0 while the dialog was hidden.
      swiper.update()
      if (swiper.activeIndex !== index) swiper.slideTo(index, 0)
    }
  }, [index])

  const handleCancel = (e: SyntheticEvent<HTMLDialogElement>) => {
    e.preventDefault() // Esc: let the route state close it
    onClose()
  }

  const handleClick = (e: MouseEvent<HTMLDialogElement>) => {
    if (swiperRef.current && !swiperRef.current.allowClick) return // end of a swipe
    if (e.target instanceof Element && e.target.closest(KEEP_OPEN)) return
    onClose()
  }

  return (
    <dialog
      ref={dialogRef}
      className="section-dialog"
      aria-labelledby="section-dialog-title"
      onCancel={handleCancel}
      onClick={handleClick}
    >
      <header className="section-dialog__header">
        <div className="section-dialog__label">
          <h2 id="section-dialog-title" className="section-dialog__title">
            {sections[shown].title}
          </h2>
          <span className="section-dialog__count">
            {shown + 1} / {sections.length}
          </span>
        </div>
        <button type="button" className="section-dialog__close" aria-label="Đóng" onClick={onClose}>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </header>

      <div className="section-dialog__stage">
        <Swiper
          modules={[A11y, Keyboard, Navigation, Zoom]}
          initialSlide={shown}
          keyboard={{ enabled: true }}
          navigation
          zoom={{ maxRatio: 3 }}
          observer
          observeParents
          a11y={{
            prevSlideMessage: 'Mục trước',
            nextSlideMessage: 'Mục sau',
            firstSlideMessage: 'Đây là mục đầu',
            lastSlideMessage: 'Đây là mục cuối',
          }}
          onSwiper={(swiper) => {
            swiperRef.current = swiper
          }}
          onSlideChange={(swiper) => {
            if (index !== null && swiper.activeIndex !== index) onChange(swiper.activeIndex)
          }}
        >
          {sections.map((section, i) => (
            <SwiperSlide key={section.slug}>
              <div className="swiper-zoom-container">
                <SectionPage section={section} active={index === i} />
              </div>
              <div className="swiper-lazy-preloader swiper-lazy-preloader-white" />
            </SwiperSlide>
          ))}
        </Swiper>
      </div>

      <ButterflyBurst burst={burst} />
    </dialog>
  )
}
