import { useEffect, useMemo, useRef, useState, type DragEvent, type ReactNode } from 'react'
import { activities, faq, programs, translations, type Category, type DocRecord, type Lang, type Notice } from './data'
import * as api from './api'
import type { ApiNotice, ApiDocument, ApiInquiry, ApiGalleryItem, DashboardData, UploadedFile, UserInfo } from './api'

const HERO_ART = '/assets/hero-full.webp'
const GALLERY_ART = '/assets/gallery-classroom.webp'
const MAPS_URL = 'https://maps.app.goo.gl/1PW44EVbxNpbGBfC8'

const iconPaths: Record<string, string> = {
  star: 'M12 2.8l2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 2.8z',
  arrow: 'M4 12h15m-6-6 6 6-6 6',
  chevron: 'm6 9 6 6 6-6',
  menu: 'M4 7h16M4 12h16M4 17h16',
  close: 'M6 6l12 12M18 6 6 18',
  search: 'm21 21-4.3-4.3m2.3-5.2a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0z',
  filter: 'M4 6h16M7 12h10m-7 6h4',
  phone: 'M7.4 3.5 5.2 4.7c-.8.5-.9 1.6-.6 2.6 1.3 4.2 4 7.1 8.4 8.8 1 .4 2.1.2 2.7-.6l1.3-2.1-3.1-2.1-1.4 1.3a11.8 11.8 0 0 1-3.7-3.6l1.3-1.4-2.7-3.9z',
  mail: 'M4 6.5h16v11H4zM4 7l8 6 8-6',
  pin: 'M12 21s6-5.4 6-11a6 6 0 1 0-12 0c0 5.6 6 11 6 11zm0-8.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
  play: 'm8 5 11 7-11 7V5z',
  heart: 'M20.8 8.8c0 5-8.8 10.2-8.8 10.2S3.2 13.8 3.2 8.8a4.7 4.7 0 0 1 8.8-2.3 4.7 4.7 0 0 1 8.8 2.3z',
  book: 'M5 4.5c2.5-.8 4.8-.2 7 1.2v14c-2.2-1.4-4.5-2-7-1.2v-14zm14 0c-2.5-.8-4.8-.2-7 1.2v14c2.2-1.4 4.5-2 7-1.2v-14z',
  brush: 'm4 17 9.5-9.5 3 3L7 20H4v-3zm8.7-10.7 2-2 3 3-2 2-3-3z',
  blocks: 'M4 12h6V6H4v6zm8 6h8v-6h-8v6zm0-12h8v-4h-8v4zM4 20h6v-6H4v6z',
  music: 'M9 18V5l10-2v13M9 18a3 3 0 1 1-3-3 3 3 0 0 1 3 3zm10-2a3 3 0 1 1-3-3 3 3 0 0 1 3 3z',
  sparkle: 'm12 2 1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5L12 2zM19 16l.7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16z',
  file: 'M6 3h8l4 4v14H6V3zm8 0v5h4M9 12h6M9 16h6',
  pdf: 'M6 3h8l4 4v14H6V3zm8 0v5h4M8.5 16h1.2a1.5 1.5 0 0 0 0-3H8.5v6m5-6v6m0-3h2',
  image: 'M4 5h16v14H4V5zm2 11 3.5-3.5 2.6 2.4 2-2 3.9 3.1M15.5 9.2h.1',
  download: 'M12 4v11m0 0 4-4m-4 4-4-4M5 20h14',
  external: 'M14 4h6v6m-1-5L11 13M18 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h5',
  bell: 'M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 22h4',
  dashboard: 'M4 4h6v7H4V4zm10 0h6v4h-6V4zM4 15h6v5H4v-5zm10-4h6v9h-6v-9z',
  notice: 'M4 5h16v12H8l-4 4V5zm4 4h8m-8 4h5',
  upload: 'M12 16V4m0 0L8 8m4-4 4 4M5 19h14',
  settings: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm0-5v2m0 13v2M3.5 12h2m13 0h2M5.9 5.9l1.4 1.4m9.4 9.4 1.4 1.4m0-12.2-1.4 1.4M7.3 16.7l-1.4 1.4',
  logout: 'M10 4H5v16h5m5-4 4-4-4-4m4 4H9',
  plus: 'M12 5v14M5 12h14',
  edit: 'M4 20h4L19 9l-4-4L4 16v4zm9.5-13.5 4 4',
  eye: 'M2.5 12s3.3-5 9.5-5 9.5 5 9.5 5-3.3 5-9.5 5-9.5-5-9.5-5zm9.5 2a2 2 0 1 0 0-4 2 2 0 0 0 0 4z',
  eyeOff: 'M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22',
  trash: 'M5 7h14m-9 4v5m4-5v5M9 7V4h6v3m-9 0 1 14h10l1-14',
  calendar: 'M5 5h14v15H5V5zm3-2v4m8-4v4M5 9h14',
  link: 'M10 13a5 5 0 0 0 7.1.1l1.4-1.4a5 5 0 0 0-7.1-7.1L10 6m4 5a5 5 0 0 0-7.1-.1l-1.4 1.4a5 5 0 0 0 7.1 7.1L14 18',
  heading: 'M4 6h16M4 12h10M4 18h16',
  bold: 'M7 4h5a3 3 0 0 1 0 6H7V4zm0 6h6a3 3 0 0 1 0 6H7v-6z',
  italic: 'M10 4h7M7 20h7m-4-16L9 20',
  underline: 'M6 4v5a6 6 0 0 0 12 0V4M5 20h14',
  undo: 'M9 7 4 12l5 5M5 12h8a6 6 0 0 1 6 6',
  redo: 'm15 7 5 5-5 5m4-5h-8a6 6 0 0 0-6 6',
  list: 'M8 6h12M8 12h12M8 18h12M4 6h.1M4 12h.1M4 18h.1',
  check: 'm5 12 4 4L19 6',
  info: 'M12 17v-5m0-4h.1M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z',
  message: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z',
  copy: 'M8 4v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7.414A2 2 0 0 0 19.414 6L16 2.586A2 2 0 0 0 14.586 2H10a2 2 0 0 0-2 2zm-4 4v12a2 2 0 0 0 2 2h8',
  lock: 'M19 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2zm-7-8a4 4 0 0 0-4 4v4h8V7a4 4 0 0 0-4-4z',
}

function Icon({ name, size = 18, stroke = 1.8 }: { name: string; size?: number; stroke?: number }) {
  return <svg aria-hidden="true" className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round"><path d={iconPaths[name] ?? iconPaths.sparkle} /></svg>
}

function Logo({ compact = false }: { compact?: boolean }) {
  return <div className={`brand-lockup ${compact ? 'brand-lockup--compact' : ''}`} aria-label="Little Star Playhouse">
    <img className="brand-logo-image" src="/assets/little-star-playhouse-logo.png" alt="Little Star Playhouse — A safe place for little stars to shine." />
  </div>
}

function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  return <div className="toast" role="status"><Icon name="check" size={17} /><span>{message}</span><button aria-label="Close notification" onClick={onClose}><Icon name="close" size={15} /></button></div>
}

function SiteHeader({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  const [open, setOpen] = useState(false)
  const t = translations[lang]
  const navItems = [['/', t.nav.home], ['/about', t.nav.about], ['/programs', t.nav.programs], ['/our-little-world', t.nav.world], ['/gallery', t.nav.gallery], ['/notices', t.nav.notices], ['/documents', t.nav.documents]]
  const go = (path: string) => { setOpen(false); onNavigate(path) }
  return <>
    <div className="announcement"><span><Icon name="sparkle" size={14} /> A little world of learning is waiting in Janakpurdham.</span><button onClick={() => go('/contact')}>Visit us <Icon name="arrow" size={14} /></button></div>
    <header className="site-header">
      <div className="shell header-inner"><button className="logo-button" onClick={() => go('/')}><Logo /></button><nav className={`site-nav ${open ? 'site-nav--open' : ''}`}>{navItems.map(([path, label]) => <button key={path} className={window.location.pathname === path ? 'is-active' : ''} onClick={() => go(path)}>{label}</button>)}<div className="nav-mobile-actions"><button className="lang-switch" onClick={() => setLang(lang === 'en' ? 'ne' : 'en')}><span className={lang === 'en' ? 'active' : ''}>EN</span><span>/</span><span className={lang === 'ne' ? 'active' : ''}>ने</span></button><a className="button button--small header-enquire" href="/contact" onClick={event => { event.preventDefault(); go('/contact') }}>{t.actions.headerEnquire} <Icon name="arrow" size={15} /></a></div></nav><div className="header-actions"><button className="lang-switch" onClick={() => setLang(lang === 'en' ? 'ne' : 'en')}><span className={lang === 'en' ? 'active' : ''}>EN</span><span>/</span><span className={lang === 'ne' ? 'active' : ''}>ने</span></button><a className="button button--small header-enquire" href="/contact" onClick={event => { event.preventDefault(); go('/contact') }}>{t.actions.headerEnquire} <Icon name="arrow" size={15} /></a><button className="menu-button" aria-label="Open menu" aria-expanded={open} onClick={() => setOpen(!open)}><Icon name={open ? 'close' : 'menu'} size={22} /></button></div></div>
    </header>
  </>
}

function Footer({ lang, onNavigate }: { lang: Lang; onNavigate: (path: string) => void }) {
  const t = translations[lang]
  return <footer className="site-footer"><div className="shell footer-grid"><div><button className="footer-logo" onClick={() => onNavigate('/')}><Logo /></button><p>A caring, joyful place where little learners explore, discover confidence, and grow through play.</p><div className="footer-socials"><a href="https://wa.me/9779709142797" aria-label="WhatsApp"><span>WA</span></a><a href="mailto:littlestarplayhouse2026@gmail.com" aria-label="Email"><Icon name="mail" size={17} /></a><a href="tel:+9779709142797" aria-label="Call"><Icon name="phone" size={17} /></a></div></div><div><h4>Explore</h4><button onClick={() => onNavigate('/about')}>{t.nav.about}</button><button onClick={() => onNavigate('/programs')}>{t.nav.programs}</button><button onClick={() => onNavigate('/our-little-world')}>{t.nav.world}</button><button onClick={() => onNavigate('/notices')}>{t.nav.notices}</button></div><div><h4>Parent shelf</h4><button onClick={() => onNavigate('/documents')}>{t.nav.documents}</button><button onClick={() => onNavigate('/contact')}>{t.actions.enquire}</button><button onClick={() => window.open(MAPS_URL, '_blank')}>{t.actions.directions}</button><button onClick={() => onNavigate('/admin')}>{t.nav.admin}</button></div><div><h4>Come say hello</h4><p className="footer-address">Ward 4, Janakpurdham,<br />Dhanusha, Nepal<br /><span>Near the old Sanchaykosh Office, on the way to Kataiyachauri.</span></p><a href="tel:+9779709142797">9709142797</a><a href="mailto:littlestarplayhouse2026@gmail.com">littlestarplayhouse2026@gmail.com</a></div></div><div className="shell footer-bottom"><span>© 2026 Little Star Playhouse</span><span>A safe place for little stars to shine.</span></div></footer>
}

function PublicShell({ children, lang, setLang, onNavigate }: { children: ReactNode; lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  return <><SiteHeader lang={lang} setLang={setLang} onNavigate={onNavigate} />{children}<Footer lang={lang} onNavigate={onNavigate} /></>
}

function SectionLabel({ children, tone = 'blue' }: { children: ReactNode; tone?: string }) { return <span className={`section-label section-label--${tone}`}><i />{children}</span> }
function PageIntro({ eyebrow, title, text, tone = 'blue' }: { eyebrow: string; title: string; text: string; tone?: string }) { return <section className={`page-intro page-intro--${tone}`}><div className="shell page-intro-inner"><div><SectionLabel tone={tone}>{eyebrow}</SectionLabel><h1>{title}</h1><p>{text}</p></div><div className="intro-orbit"><span className="orbit-star"><Icon name="star" size={30} /></span><span className="orbit-cloud" /><span className="orbit-dot orbit-dot--one" /><span className="orbit-dot orbit-dot--two" /></div></div></section> }
function Button({ children, onClick, variant = 'primary', type = 'button', disabled = false, className = '' }: { children: ReactNode; onClick?: () => void; variant?: 'primary' | 'outline' | 'soft' | 'text' | 'danger'; type?: 'button' | 'submit'; disabled?: boolean; className?: string }) { return <button type={type} disabled={disabled} className={`button button--${variant} ${className}`} onClick={onClick}>{children}</button> }

function Hero({ lang, onNavigate }: { lang: Lang; onNavigate: (path: string) => void }) {
  const t = translations[lang]
  return <section className="hero"><div className="hero-cloud hero-cloud--one" /><div className="hero-cloud hero-cloud--two" /><div className="shell hero-grid"><div className="hero-copy"><SectionLabel tone="yellow">Little Star Playhouse · Janakpurdham</SectionLabel><h1>Big dreams begin with <span>little steps!</span></h1><p>A caring, joyful place where little learners explore, discover their confidence, and grow through play.</p><div className="hero-actions"><Button onClick={() => onNavigate('/contact')}>{t.actions.enquire} <Icon name="arrow" size={17} /></Button><Button variant="outline" onClick={() => onNavigate('/our-little-world')}><span className="play-dot"><Icon name="play" size={12} /></span>{t.actions.discover}</Button></div><div className="hero-note"><span className="avatar-stack"><i>✦</i><i>♡</i><i>●</i></span><span>Warm beginnings. Curious minds. Room to grow.</span></div></div><div className="hero-art"><div className="hero-art-frame"><img src={HERO_ART} alt="Children building and painting in a full Little Star Playhouse classroom scene" loading="eager" fetchPriority="high" decoding="async" /><div className="hero-sticker hero-sticker--top"><Icon name="star" size={17} /> play, learn, shine</div><div className="hero-sticker hero-sticker--bottom"><span className="sticker-dot" /> A happy little world</div></div></div></div><div className="hero-wave" /></section>
}

function TrustStrip() { const items = [{ icon: 'heart', title: 'Early childhood learning', text: 'Gentle foundations' }, { icon: 'play', title: 'Learning through play', text: 'Curiosity leads the way' }, { icon: 'brush', title: 'Creative exploration', text: 'Make room for wonder' }, { icon: 'star', title: 'A welcoming environment', text: 'Every little star belongs' }]; return <section className="trust-strip"><div className="shell trust-grid">{items.map(item => <div className="trust-item" key={item.title}><span className="trust-icon"><Icon name={item.icon} size={22} /></span><div><strong>{item.title}</strong><small>{item.text}</small></div></div>)}</div></section> }

function HomePage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><Hero lang={lang} onNavigate={onNavigate} /><TrustStrip /><section className="section about-home"><div className="shell split-grid"><div className="photo-card photo-card--tall"><img src={GALLERY_ART} alt="Children exploring blocks and art materials in a warm classroom" loading="lazy" /><span className="photo-note"><Icon name="sparkle" size={15} /> little moments, big meaning</span></div><div className="section-copy"><SectionLabel tone="green">A place to grow into</SectionLabel><h2>Little steps.<br /><span>Big discoveries.</span></h2><p>Little Star Playhouse is a caring space for young learners to feel safe, seen, and excited about the world around them. We make space for stories, messy making, music, movement, and the small moments that build confidence.</p><p>Our days are shaped by warm relationships and playful invitations, so every child can find their own way to join in.</p><Button variant="text" onClick={() => onNavigate('/about')}>Meet our playhouse <Icon name="arrow" size={16} /></Button><div className="margin-note"><span>01</span><p>“A safe place for little stars to shine.”</p></div></div></div></section><ProgramsPreview lang={lang} onNavigate={onNavigate} /><WorldPreview onNavigate={onNavigate} /><GalleryPreview /><HomeNoticePreview onNavigate={onNavigate} /><AdmissionCTA lang={lang} onNavigate={onNavigate} /><FAQPreview /><ContactPreview lang={lang} onNavigate={onNavigate} /></PublicShell>
}

function HomeNoticePreview({ onNavigate }: { onNavigate: (path: string) => void }) {
  const [items, setItems] = useState<ApiNotice[]>([])
  const [error, setError] = useState(false)
  const load = () => api.getPublicNotices({ page_size: 3 }).then(result => { setItems(result.items); setError(false) }).catch(() => setError(true))
  useEffect(() => { load() }, [])
  return <section className="section"><div className="shell"><div className="section-heading-row"><div><SectionLabel tone="blue">From the school</SectionLabel><h2>Recent <span>notices.</span></h2></div><Button variant="text" onClick={() => onNavigate('/notices')}>All notices <Icon name="arrow" size={16} /></Button></div>{error ? <div role="alert" className="upload-error">Recent notices could not be loaded. <Button variant="outline" onClick={load}>Retry</Button></div> : items.length ? <div className="notice-feed">{items.map(notice => <NoticeCard key={notice.id} notice={notice} onNavigate={onNavigate} />)}</div> : <p>No published notices yet.</p>}</div></section>
}

function ProgramsPreview({ lang, onNavigate }: { lang: Lang; onNavigate: (path: string) => void }) { const t = translations[lang]; return <section className="section section--pale-blue"><div className="shell"><div className="section-heading-row"><div><SectionLabel tone="blue">Find your little rhythm</SectionLabel><h2>Programs made for <span>curious beginnings.</span></h2></div><Button variant="text" onClick={() => onNavigate('/programs')}>{t.actions.explore} <Icon name="arrow" size={16} /></Button></div><div className="program-grid">{programs.map((program, index) => <article className={`program-card program-card--${program.color}`} key={program.title}><div className="program-art"><img src={program.image} alt={`${program.title} activity`} loading="lazy" /><span className="program-art-overlay" /><span className="program-icon"><Icon name={program.icon} size={25} /></span><span className="program-number">0{index + 1}</span><div className="program-shape program-shape--one" /><div className="program-shape program-shape--two" /></div><div className="program-content"><span className="program-age">{program.age}</span><h3>{program.title}</h3><p>{program.text}</p><button onClick={() => onNavigate('/programs')}>Explore program <Icon name="arrow" size={15} /></button></div></article>)}</div></div></section> }
function WorldPreview({ onNavigate }: { onNavigate: (path: string) => void }) { return <section className="section world-preview"><div className="shell"><div className="section-heading-row"><div><SectionLabel tone="yellow">Come play with us</SectionLabel><h2>Our little world is full of <span>bright ideas.</span></h2></div><Button variant="text" onClick={() => onNavigate('/our-little-world')}>See all activities <Icon name="arrow" size={16} /></Button></div><div className="activity-mosaic">{activities.map(item => <article className={`activity-card activity-card--${item.color} ${item.wide ? 'activity-card--wide' : ''}`} key={item.title}><span className="activity-icon"><Icon name={item.icon} size={23} /></span><div><h3>{item.title}</h3><p>{item.text}</p></div><span className="activity-arrow"><Icon name="arrow" size={16} /></span></article>)}</div></div></section> }
function GalleryPreview() {
  const [items, setItems] = useState<ApiGalleryItem[]>([])
  const [selected, setSelected] = useState<ApiGalleryItem | null>(null)
  useEffect(() => { api.getGallery().then(result => setItems(result.items)).catch(() => setItems([])) }, [])
  const open = (item: ApiGalleryItem) => setSelected(item)
  return <section className="section gallery-section"><div className="shell">
    <div className="section-heading-row"><div><SectionLabel tone="coral">A peek inside</SectionLabel><h2>Little moments from <span>our happy days.</span></h2></div><span className="gallery-caption"><Icon name="image" size={16} /> {items.length ? `${items.length} moments` : 'A little glimpse of play'}</span></div>
    {items.length ? <div className="gallery-live-grid">{items.map(item => <button className="gallery-live-card" key={item.id} onClick={() => open(item)}><img src={api.absoluteApiUrl(item.image_url)} alt={item.caption} loading="lazy" /><span>{item.caption}</span></button>)}</div> : <div className="gallery-grid"><div className="gallery-tile gallery-tile--large gallery-tile-button" role="button" tabIndex={0} onClick={() => setSelected({ id: 'preview', file_id: '', caption: 'Building and discovery', image_url: GALLERY_ART, created_at: '' })} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') setSelected({ id: 'preview', file_id: '', caption: 'Building and discovery', image_url: GALLERY_ART, created_at: '' }) }} aria-label="Open classroom image preview"><img src={GALLERY_ART} alt="Children creating with blocks and art supplies" loading="lazy" /><span>Building and discovery · View larger</span></div><div className="gallery-tile gallery-tile--yellow"><span className="gallery-doodle"><Icon name="star" size={35} /></span><strong>Make<br />room for<br /><em>wonder.</em></strong></div><div className="gallery-tile gallery-tile--blue"><span className="gallery-doodle"><Icon name="music" size={32} /></span><strong>Sing it,<br />move it,<br /><em>feel it.</em></strong></div></div>}
  </div>{selected && <div className="lightbox" role="dialog" aria-modal="true" aria-label={selected.caption} onClick={() => setSelected(null)}><div className="lightbox-card" onClick={event => event.stopPropagation()}><button className="lightbox-close" aria-label="Close image preview" onClick={() => setSelected(null)}><Icon name="close" size={20} /></button><img src={selected.id === 'preview' ? selected.image_url : api.absoluteApiUrl(selected.image_url)} alt={selected.caption} /><p>{selected.caption}</p></div></div>}</section>
}
function AdmissionCTA({ lang, onNavigate }: { lang: Lang; onNavigate: (path: string) => void }) { const t = translations[lang]; return <section className="admission-section"><div className="shell admission-card"><div className="admission-stars"><Icon name="star" size={22} /><Icon name="star" size={13} /><Icon name="star" size={17} /></div><div><SectionLabel tone="yellow">A happy next chapter</SectionLabel><h2>Your child’s next happy chapter <span>starts here!</span></h2><p>Have a question, a little one ready to explore, or simply want to say hello? We would love to hear from you.</p></div><div className="admission-actions"><Button onClick={() => window.open('https://wa.me/9779709142797', '_blank')}>{t.actions.whatsapp} <Icon name="arrow" size={16} /></Button><Button variant="outline" onClick={() => onNavigate('/contact')}>{t.actions.call} <Icon name="phone" size={16} /></Button></div></div></section> }
function FAQPreview() { const [open, setOpen] = useState(0); return <section className="section faq-section"><div className="shell split-grid split-grid--faq"><div className="section-copy"><SectionLabel tone="blue">The little things</SectionLabel><h2>Questions are <span>welcome here.</span></h2><p>Starting something new can bring a lot of questions. Here are a few gentle answers to get you started.</p><div className="faq-badge"><Icon name="sparkle" size={19} /><span>Still curious?</span><a href="mailto:littlestarplayhouse2026@gmail.com">Ask us anything <Icon name="arrow" size={14} /></a></div></div><div className="faq-list">{faq.map((item, index) => <div className={`faq-item ${open === index ? 'is-open' : ''}`} key={item.q}><button onClick={() => setOpen(open === index ? -1 : index)} aria-expanded={open === index}><span>{item.q}</span><span className="faq-plus"><Icon name={open === index ? 'close' : 'plus'} size={17} /></span></button>{open === index && <p>{item.a}</p>}</div>)}</div></div></section> }
function ContactPreview({ lang, onNavigate }: { lang: Lang; onNavigate: (path: string) => void }) { const t = translations[lang]; return <section className="contact-preview"><div className="shell contact-preview-inner"><div><SectionLabel tone="yellow">Come say hello</SectionLabel><h2>We’re right here in <span>Janakpurdham.</span></h2><p>Ward 4, Dhanusha, Nepal<br />Near the old Sanchaykosh Office, on the way to Kataiyachauri.</p></div><div className="contact-actions"><a href="tel:+9779709142797"><Icon name="phone" size={18} />9709142797</a><a href="mailto:littlestarplayhouse2026@gmail.com"><Icon name="mail" size={18} />Email the playhouse</a><Button variant="outline" onClick={() => window.open(MAPS_URL, '_blank')}>{t.actions.directions} <Icon name="arrow" size={16} /></Button></div></div></section> }

function AboutPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) { return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="The heart of the playhouse" title="A safe place for little stars to shine." text="We believe the early years deserve patience, wonder, and lots of room to become." tone="green" /><section className="section"><div className="shell split-grid"><div className="section-copy"><SectionLabel tone="green">Our philosophy</SectionLabel><h2>Childhood is not a race. <span>It is a world.</span></h2><p>At Little Star Playhouse, learning begins with belonging. Our environment is designed to help children feel safe enough to wonder, brave enough to try, and supported enough to keep going.</p><p>We use play, conversation, movement, making, and warm relationships as invitations into learning. The details are little, but the discoveries are big.</p><div className="values-row"><div><strong>01</strong><span>Warm relationships</span></div><div><strong>02</strong><span>Playful learning</span></div><div><strong>03</strong><span>Growing confidence</span></div></div></div><div className="story-card story-card--green"><div className="story-card-star"><Icon name="star" size={32} /></div><h3>Little Star<br /><span>promise</span></h3><p>Every child deserves a place where their questions are welcome and their small steps are celebrated.</p><div className="story-card-line" /></div></div></section><AdmissionCTA lang="en" onNavigate={onNavigate} /></PublicShell> }
function ProgramsPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) { return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="Find your little rhythm" title="Programs that grow with curiosity." text="Every program is an invitation: to play, to make, to move, and to discover what comes next." tone="blue" /><section className="section section--pale-yellow"><div className="shell program-grid program-grid--page">{programs.map((program, index) => <article className={`program-card program-card--${program.color}`} key={program.title}><div className="program-art"><img src={program.image} alt={`${program.title} activity`} loading="lazy" /><span className="program-art-overlay" /><span className="program-icon"><Icon name={program.icon} size={25} /></span><span className="program-number">0{index + 1}</span><div className="program-shape program-shape--one" /><div className="program-shape program-shape--two" /></div><div className="program-content"><span className="program-age">{program.age}</span><h3>{program.title}</h3><p>{program.text}</p><ul><li><Icon name="check" size={15} />Stories and shared conversation</li><li><Icon name="check" size={15} />Hands-on creative invitations</li><li><Icon name="check" size={15} />Gentle routines that build confidence</li></ul><Button variant="text" onClick={() => onNavigate('/contact')}>Ask about this program <Icon name="arrow" size={15} /></Button></div></article>)}</div></section><AdmissionCTA lang="en" onNavigate={onNavigate} /></PublicShell> }
function WorldPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) { return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="Come play with us" title="Our little world is full of bright ideas." text="A playful day can hold a story, a song, a tower, a paintbrush, and a hundred ways to wonder." tone="yellow" /><section className="section"><div className="shell activity-mosaic activity-mosaic--page">{activities.map(item => <article className={`activity-card activity-card--${item.color} ${item.wide ? 'activity-card--wide' : ''}`} key={item.title}><span className="activity-icon"><Icon name={item.icon} size={25} /></span><div><h3>{item.title}</h3><p>{item.text}</p><p className="activity-long">We make space for children to follow their interests, share ideas, and find their own way into the invitation.</p></div><span className="activity-arrow"><Icon name="arrow" size={17} /></span></article>)}</div></section><GalleryPreview /></PublicShell> }

function ContactPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  const t = translations[lang]
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [program, setProgram] = useState('Playgroup')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')
    try {
      const res = await api.submitInquiry({
        parent_name: name,
        phone,
        email: email || undefined,
        program,
        message,
        website: e.currentTarget.querySelector<HTMLInputElement>('[name="website"]')?.value || '',
      })
      setSuccess(res.message || 'Thank you for reaching out! We have received your inquiry.')
      setName('')
      setPhone('')
      setEmail('')
      setMessage('')
    } catch (err: any) {
      setError(err.detail || 'Unable to submit your enquiry right now. Please call or WhatsApp us.')
    } finally {
      setLoading(false)
    }
  }

  return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="We’d love to hear from you" title="Come say hello to the playhouse." text="Questions, directions, admission enquiries, or a simple hello — there is always room for a good conversation." tone="coral" /><section className="section"><div className="shell contact-page-grid"><div className="contact-detail-card"><SectionLabel tone="blue">Find us here</SectionLabel><h2>Little Star<br /><span>Playhouse</span></h2><p>Ward 4, Janakpurdham, Dhanusha, Nepal</p><p className="muted">Near the old Sanchaykosh Office, on the way to Kataiyachauri.</p><div className="contact-detail-list"><a href="tel:+9779709142797"><span><Icon name="phone" size={19} /></span><div><small>Phone</small><strong>9709142797</strong></div></a><a href="mailto:littlestarplayhouse2026@gmail.com"><span><Icon name="mail" size={19} /></span><div><small>Email</small><strong>littlestarplayhouse2026@gmail.com</strong></div></a></div><div className="contact-detail-actions"><Button onClick={() => window.open('https://wa.me/9779709142797', '_blank')}>WhatsApp <Icon name="arrow" size={15} /></Button><Button variant="outline" onClick={() => window.open(MAPS_URL, '_blank')}>Get directions <Icon name="pin" size={16} /></Button></div></div><div className="enquiry-card"><SectionLabel tone="yellow">Start a conversation</SectionLabel><h2>Tell us a little <span>about your question.</span></h2>{success && <div className="mock-banner mock-banner--green"><Icon name="check" size={18} /><span>{success}</span></div>}{error && <div className="upload-error"><Icon name="info" size={18} /><span>{error}</span></div>}        <form onSubmit={handleSubmit}>
          <label>Your name<input required value={name} onChange={e => setName(e.target.value)} placeholder="A parent or carer name" /></label>
          <label>Phone number<input required value={phone} onChange={e => setPhone(e.target.value)} placeholder="+977 98XXXXXXXX" /></label>
          <label>Email (optional)<input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" /></label>
          <label>Program of interest
            <div className="select-wrap">
              <select value={program} onChange={e => setProgram(e.target.value)}>
                <option value="Playgroup">Playgroup</option>
                <option value="Nursery Readiness">Nursery Readiness</option>
                <option value="Creative Play">Creative Play</option>
                <option value="General Enquiry">General Enquiry</option>
              </select>
              <span className="select-arrow" aria-hidden="true"><Icon name="chevron" size={16} /></span>
            </div>
          </label>
          <label className="enquiry-field--full">What can we help with?
            <textarea required rows={4} value={message} onChange={e => setMessage(e.target.value)} placeholder="I would love to ask about…" />
          </label>
          <input type="text" name="website" tabIndex={-1} autoComplete="off" aria-hidden="true" style={{ position: 'absolute', left: '-10000px', width: 1, height: 1 }} />
          <Button type="submit" disabled={loading}>{loading ? 'Sending enquiry...' : 'Send enquiry'} <Icon name="arrow" size={16} /></Button>
          <small className="form-note">Your enquiry connects directly to Little Star Playhouse administration.</small>
        </form></div></div></section></PublicShell>
}

function FilterBar({ value, setValue, categories, placeholder }: { value: string; setValue: (value: string) => void; categories: string[]; placeholder: string }) { return <div className="filter-bar"><div className="search-field"><Icon name="search" size={18} /><input value={value} onChange={event => setValue(event.target.value)} placeholder={placeholder} aria-label={placeholder} /></div><div className="filter-chips">{categories.map(category => <button className={value === category ? 'is-selected' : ''} key={category} onClick={() => setValue(value === category ? '' : category)}><Icon name={category === 'All' ? 'sparkle' : 'filter'} size={14} />{category}</button>)}</div></div> }

function NoticeCard({ notice, onNavigate }: { notice: any; onNavigate: (path: string) => void }) {
  const cover = notice.cover || (notice.cover_image_url ? api.absoluteApiUrl(notice.cover_image_url) : undefined)
  const idOrSlug = notice.slug || notice.id
  return <article className="notice-card"><div className="notice-card-head"><div className="mini-brand"><span><Icon name="star" size={15} /></span><div><strong>Little Star Playhouse</strong><small>{notice.published_at ? new Date(notice.published_at).toLocaleDateString() : notice.date || 'School Announcement'}</small></div></div><button className="more-button" aria-label="More notice actions" onClick={() => onNavigate(`/notices/${idOrSlug}`)}>•••</button></div>{cover && <div className="notice-cover"><img src={cover} alt="" loading="lazy" /><div className="notice-cover-badge"><Icon name={notice.category === 'Events' ? 'calendar' : 'bell'} size={14} /> {notice.category}</div></div>}<div className="notice-card-body"><div className="notice-tags"><span className={`tag tag--${notice.is_important || notice.important ? 'important' : 'blue'}`}>{(notice.is_important || notice.important) && <Icon name="star" size={12} />}{notice.category}</span>{(notice.is_pinned || notice.pinned) && <span className="tag tag--outline"><Icon name="pin" size={12} /> Pinned</span>}</div><h2>{notice.title}</h2><p>{notice.excerpt}</p><div className="notice-card-foot"><span>{notice.author?.display_name || notice.author || 'Playhouse Team'}</span><button onClick={() => onNavigate(`/notices/${idOrSlug}`)}>Read full notice <Icon name="arrow" size={15} /></button></div></div>{notice.attachments && notice.attachments.length > 0 && <div className="notice-attachments">{notice.attachments.map((file: any) => <AttachmentCard key={file.id || file.name} file={file} compact />)}</div>}</article>
}

function AttachmentCard({ file, compact = false }: { file: any; compact?: boolean }) {
  const name = file.filename || file.name
  const type = file.type || file.attachment_type || 'file'
  const size = file.size ? (typeof file.size === 'number' ? `${(file.size / 1024).toFixed(0)} KB` : file.size) : ''
  const dlUrl = file.download_url ? api.absoluteApiUrl(file.download_url) : '#'
  return <div className={`attachment-card ${compact ? 'attachment-card--compact' : ''}`}><span className={`file-icon file-icon--${type}`}><Icon name={type.includes('image') ? 'image' : type.includes('pdf') ? 'pdf' : 'file'} size={18} /></span><div><strong>{name}</strong><small>{type.toUpperCase()} {size ? `· ${size}` : ''}</small></div><a href={dlUrl} target="_blank" rel="noreferrer" aria-label={`Download ${name}`} className="button button--small button--soft"><Icon name="download" size={16} /></a></div>
}

function NoticesPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  const t = translations[lang]
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [visible, setVisible] = useState(6)
  const [liveNotices, setLiveNotices] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const loadNotices = () => {
    setLoading(true)
    setLoadError('')
    const apiCategory = category === 'General Announcements' ? 'General' : category === 'Important' ? 'Important' : category || undefined
    api.getPublicNotices({ page_size: 50, search: query, category: apiCategory })
      .then(res => setLiveNotices(res.items))
      .catch(() => setLoadError('Notices could not be loaded. Check your connection and try again.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadNotices()
  }, [query, category])

  const filters: string[] = [t.labels.all, t.labels.important, t.labels.general, t.labels.events, t.labels.holidays, t.labels.docs]
  const displayNotices = liveNotices

  return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="Stay in the loop" title="What’s Happening at Little Star?" text="Stay up to date with school announcements, important information, events, and helpful resources for parents." tone="blue" /><main className="section section--feed"><div className="shell"><FilterBar value={query || category} setValue={value => { if (filters.includes(value)) { setCategory(value); setQuery('') } else { setQuery(value); setCategory('') } }} categories={filters} placeholder={`${t.labels.search} notices`} />{loading ? <p role="status">Loading notices…</p> : loadError ? <div role="alert" className="upload-error">{loadError} <Button variant="outline" onClick={loadNotices}>Retry</Button></div> : displayNotices.length === 0 ? <EmptyState title={t.labels.noResults} text={t.labels.noResultsText} /> : <div className="notice-feed">{displayNotices.slice(0, visible).map(notice => <NoticeCard key={notice.id} notice={notice} onNavigate={onNavigate} />)}</div>}{!loading && !loadError && visible < displayNotices.length && <div className="load-more"><Button variant="outline" onClick={() => setVisible(visible + 4)}>Load more notices <Icon name="arrow" size={15} /></Button></div>}</div></main></PublicShell>
}

function NoticeDetailPage({ id, lang, setLang, onNavigate }: { id: string; lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  const [notice, setNotice] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(false)
  const [shared, setShared] = useState(false)

  useEffect(() => {
    api.getPublicNotice(id)
      .then(res => setNotice(res))
      .catch(() => setLoadError(true))
      .finally(() => setLoading(false))
  }, [id])

  const share = async () => {
    if (!notice) return
    try {
      if (navigator.share) await navigator.share({ title: notice.title, text: notice.excerpt, url: window.location.href })
      else await navigator.clipboard.writeText(window.location.href)
      setShared(true)
    } catch { setShared(false) }
  }

  if (loading) {
    return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><main className="detail-page"><div className="shell"><p>Loading notice...</p></div></main></PublicShell>
  }

  if (!notice) return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><main className="detail-page"><div className="shell"><button className="back-link" onClick={() => onNavigate('/notices')}><Icon name="arrow" size={16} /> Back to notices</button><EmptyState title={loadError ? 'Notice unavailable' : 'That notice has moved on'} text={loadError ? 'We could not reach the notice service. Please try again.' : 'We could not find a published notice at this address. Return to the notices shelf to keep exploring.'} />{loadError && <Button variant="outline" onClick={() => { setLoading(true); setLoadError(false); api.getPublicNotice(id).then(setNotice).catch(() => setLoadError(true)).finally(() => setLoading(false)) }}>Retry</Button>}</div></main></PublicShell>

  const cover = notice.cover || (notice.cover_image_url ? api.absoluteApiUrl(notice.cover_image_url) : undefined)
  const dateStr = notice.published_at ? new Date(notice.published_at).toLocaleDateString() : notice.date || ''

  return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><main className="detail-page"><div className="shell"><button className="back-link" onClick={() => onNavigate('/notices')}><Icon name="arrow" size={16} /> Back to notices</button><article className="detail-card"><div className="detail-top"><div><div className="notice-tags"><span className="tag tag--blue">{notice.category}</span>{(notice.is_important || notice.important) && <span className="tag tag--important"><Icon name="star" size={12} /> Important</span>}</div><h1>{notice.title}</h1><p className="detail-meta">Published {dateStr} · by {notice.author?.display_name || notice.author || 'Little Star Playhouse'}</p></div><Button variant="outline" onClick={share}><Icon name="external" size={16} /> {shared ? 'Link copied' : 'Share notice'}</Button></div>{cover && <img className="detail-cover" src={cover} alt="" /> }<div className="detail-layout"><div className="rich-content">{Array.isArray(notice.body) ? notice.body.map((paragraph: string) => <p key={paragraph}>{paragraph}</p>) : <div dangerouslySetInnerHTML={{ __html: notice.body }} />}</div><aside className="detail-aside"><h3>Attachments</h3>{notice.attachments?.length > 0 ? notice.attachments.map((file: any) => <AttachmentCard key={file.id || file.name} file={file} />) : <p className="muted">No attachments</p>}<Button variant="soft" onClick={() => onNavigate('/documents')}>Browse parent resources <Icon name="arrow" size={15} /></Button></aside></div></article></div></main></PublicShell>
}

function FileTypeIcon({ type }: { type: string }) {
  const icon = type.toLowerCase().includes('pdf') ? 'pdf' : type.toLowerCase().includes('jpg') || type.toLowerCase().includes('png') || type.toLowerCase().includes('image') ? 'image' : 'file'
  return <span className={`file-icon file-icon--${type.toLowerCase()}`}><Icon name={icon} size={19} /></span>
}

function DocumentCard({ doc, onAction }: { doc: any; onAction?: (message: string) => void }) {
  const ext = doc.file?.extension || doc.type || 'PDF'
  const size = doc.file?.file_size ? `${(doc.file.file_size / 1024).toFixed(0)} KB` : doc.size || ''
  const date = doc.published_at ? new Date(doc.published_at).toLocaleDateString() : doc.date || ''
  const dlUrl = doc.download_url ? api.absoluteApiUrl(doc.download_url) : '#'
  return <article className="document-card"><div className="document-card-top"><FileTypeIcon type={ext} /><span className={`status-dot status-dot--${(doc.status || 'published').toLowerCase()}`}>{doc.status || 'Published'}</span></div><div><span className="document-category">{doc.category}</span><h3>{doc.title}</h3><p>{doc.description}</p></div><div className="document-meta"><span>{ext.toUpperCase()} · {size}</span><span>{date}</span></div><div className="document-actions"><a href={`${dlUrl}?preview=true`} target="_blank" rel="noreferrer" className="button button--soft button--small">View <Icon name="eye" size={15} /></a><a href={dlUrl} download className="button button--text">Download <Icon name="download" size={15} /></a></div></article>
}

function GalleryPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) { return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="A peek inside" title="Little moments from our happy days." text="Take a gentle look at the curious, creative world inside Little Star Playhouse." tone="coral" /><GalleryPreview /><section className="section section--pale-yellow gallery-page-note"><div className="shell"><div className="section-copy"><SectionLabel tone="yellow">Room to wonder</SectionLabel><h2>Every day has a little <span>story to tell.</span></h2><p>From shared stories and colorful making to building, singing, and movement, our gallery celebrates the small moments that help children feel safe, seen, and ready to explore.</p><Button variant="outline" onClick={() => onNavigate('/contact')}>Ask about a visit <Icon name="arrow" size={15} /></Button></div></div></section></PublicShell> }

function DocumentsPage({ lang, setLang, onNavigate }: { lang: Lang; setLang: (lang: Lang) => void; onNavigate: (path: string) => void }) {
  const t = translations[lang]
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [sort, setSort] = useState('newest')
  const [toast, setToast] = useState('')
  const [liveDocs, setLiveDocs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const loadDocuments = () => {
    setLoading(true)
    setLoadError('')
    api.getPublicDocuments({ page_size: 50, search: query, category: category === 'All' ? undefined : category || undefined, file_type: typeFilter || undefined, sort })
      .then(res => setLiveDocs(res.items))
      .catch(() => setLoadError('Documents could not be loaded. Check your connection and try again.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadDocuments()
  }, [query, category, typeFilter, sort])

  const cats = ['All', 'Forms', 'School Circulars', 'Parent Guidelines', 'Event Documents', 'Learning Resources', 'Other Documents']
  const types = ['All file types', 'PDF', 'DOCX', 'JPG']
  const displayDocs = liveDocs

  return <PublicShell lang={lang} setLang={setLang} onNavigate={onNavigate}><PageIntro eyebrow="A helpful shelf for families" title="Parent Resources & Uploads" text="Find helpful school documents, forms, circulars, and resources in one convenient place." tone="green" /><main className="section section--feed"><div className="shell"><div className="document-toolbar"><div className="search-field"><Icon name="search" size={18} /><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search resources" /></div><select value={category} onChange={e => setCategory(e.target.value)} aria-label="Filter documents by category"><option value="">All categories</option>{cats.slice(1).map(cat => <option key={cat}>{cat}</option>)}</select><select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} aria-label="Filter documents by file type">{types.map(type => <option key={type} value={type === 'All file types' ? '' : type}>{type}</option>)}</select><select value={sort} onChange={e => setSort(e.target.value)} aria-label="Sort documents"><option value="newest">{t.labels.newest}</option><option value="oldest">Oldest first</option><option value="type">File type</option></select></div><div className="category-row">{cats.map(cat => <button key={cat} className={(category === cat || (!category && cat === 'All')) ? 'is-selected' : ''} onClick={() => setCategory(cat === 'All' ? '' : cat)}>{cat}</button>)}</div>{loading ? <p role="status">Loading resources…</p> : loadError ? <div role="alert" className="upload-error">{loadError} <Button variant="outline" onClick={loadDocuments}>Retry</Button></div> : displayDocs.length === 0 ? <EmptyState title="No resources found" text="Try another category, file type, or keyword and we will look again." /> : <div className="document-grid">{displayDocs.map(doc => <DocumentCard key={doc.id} doc={doc} onAction={setToast} />)}</div>}</div></main>{toast && <Toast message={toast} onClose={() => setToast('')} />}</PublicShell>
}

function EmptyState({ title, text }: { title: string; text: string }) { return <div className="empty-state"><span><Icon name="star" size={29} /></span><h3>{title}</h3><p>{text}</p></div> }

// ─── ADMIN PANEL MODULES ──────────────────────────────────────────

function AdminLogin({ onLoginSuccess, onNavigate }: { onLoginSuccess: (user: UserInfo) => void; onNavigate: (path: string) => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password) {
      setError('Please enter your username and password.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await api.login(username.trim(), password)
      onLoginSuccess(res.user)
    } catch (err: any) {
      setError(err.detail || 'Invalid username or password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-head">
          <div className="login-logo"><Logo /></div>
          <h1>Playhouse Admin</h1>
          <p>Sign in to manage announcements, documents, and parent messages.</p>
        </div>

        {error && (
          <div className="login-error" role="alert">
            <Icon name="info" size={16} />
            <span>{error}</span>
          </div>
        )}

        <form className="login-form" onSubmit={handleLogin} noValidate>
          <div className="login-field">
            <label htmlFor="admin-username">Username</label>
            <input
              id="admin-username"
              name="username"
              type="text"
              required
              autoFocus
              autoComplete="username"
              placeholder="Enter your username"
              value={username}
              onChange={e => setUsername(e.target.value)}
            />
          </div>

          <div className="login-field">
            <label htmlFor="admin-password">Password</label>
            <div className="input-with-icon">
              <input
                id="admin-password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="toggle-pwd-btn"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                onClick={() => setShowPassword(!showPassword)}
              >
                <Icon name={showPassword ? 'eyeOff' : 'eye'} size={18} />
              </button>
            </div>
          </div>

          <Button type="submit" disabled={loading} className="login-btn">
            {loading ? 'Signing in...' : 'Sign In to Workspace'} <Icon name="arrow" size={16} />
          </Button>
        </form>

        <div className="back-to-site-btn">
          <button type="button" onClick={() => onNavigate('/')}>
            <Icon name="arrow" size={14} /> Back to public website
          </button>
        </div>
      </div>
    </div>
  )
}

function AdminSidebar({ current, onNavigate, open, setOpen, user, onLogout, unreadCount }: { current: string; onNavigate: (path: string) => void; open: boolean; setOpen: (open: boolean) => void; user: UserInfo | null; onLogout: () => void; unreadCount: number }) {
  const items = [
    { path: '/admin/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { path: '/admin/messages', label: 'Messages & Enquiries', icon: 'message', badge: unreadCount > 0 ? unreadCount : undefined },
    { path: '/admin/notices', label: 'Notices', icon: 'notice' },
    { path: '/admin/notices/new', label: 'Create Notice', icon: 'plus' },
    { path: '/admin/uploads', label: 'Uploads', icon: 'upload' },
    { path: '/admin/gallery', label: 'Gallery', icon: 'image' },
    { path: '/admin/settings', label: 'Settings', icon: 'settings' },
  ]
  return <aside className={`admin-sidebar ${open ? 'is-open' : ''}`}><div className="admin-sidebar-head"><button onClick={() => onNavigate('/')}><Logo compact /></button><button className="admin-close" aria-label="Close admin menu" onClick={() => setOpen(false)}><Icon name="close" size={18} /></button></div><div className="admin-sidebar-label">Little Star admin <span>Live CMS</span></div><nav>{items.map(item => <button key={item.path} className={(current === item.path || (item.path === '/admin/dashboard' && current === '/admin')) ? 'is-active' : ''} onClick={() => { onNavigate(item.path); setOpen(false) }}><Icon name={item.icon} size={18} /><span>{item.label}</span>{item.badge && <span className="admin-badge-count">{item.badge}</span>}</button>)}</nav><div className="admin-sidebar-bottom"><div className="admin-user"><span>{user ? user.display_name.slice(0, 2).toUpperCase() : 'LS'}</span><div><strong>{user ? user.display_name : 'Administrator'}</strong><small>{user ? user.role : 'ADMIN'}</small></div></div><button onClick={() => onNavigate('/')}><Icon name="external" size={16} />View Public Site</button><button onClick={onLogout} style={{ color: 'var(--red)', marginTop: '4px' }}><Icon name="logout" size={16} />Sign Out</button></div></aside>
}

function AdminTopbar({ onOpen, onNavigate, user, unreadCount }: { onOpen: () => void; onNavigate: (path: string) => void; user: UserInfo | null; unreadCount: number }) {
  return <div className="admin-topbar"><button className="admin-menu" aria-label="Open admin menu" onClick={onOpen}><Icon name="menu" size={21} /></button><div><span className="admin-breadcrumb">Little Star Playhouse /</span><strong>Administrator Workspace</strong></div><div className="admin-top-actions"><span className="preview-pill"><i /> Secure session</span><button className="icon-button" aria-label="Notifications" onClick={() => onNavigate('/admin/messages')} style={{ position: 'relative' }}><Icon name="bell" size={19} />{unreadCount > 0 && <span style={{ position: 'absolute', top: '0', right: '0', width: '8px', height: '8px', borderRadius: '50%', background: 'var(--red)' }} />}</button><button className="admin-avatar" title={user?.username || 'Settings'} onClick={() => onNavigate('/admin/settings')}>{user ? user.display_name.slice(0, 2).toUpperCase() : 'LS'}</button></div></div>
}

function AdminLayout({ path, children, onNavigate, user, onLogout, unreadCount }: { path: string; children: ReactNode; onNavigate: (path: string) => void; user: UserInfo | null; onLogout: () => void; unreadCount: number }) {
  const [open, setOpen] = useState(false)
  return <div className="admin-shell"><AdminSidebar current={path} onNavigate={onNavigate} open={open} setOpen={setOpen} user={user} onLogout={onLogout} unreadCount={unreadCount} /><div className="admin-main"><AdminTopbar onOpen={() => setOpen(true)} onNavigate={onNavigate} user={user} unreadCount={unreadCount} /><div className="admin-content">{children}</div></div></div>
}

function AdminHeader({ eyebrow, title, text, action }: { eyebrow: string; title: string; text: string; action?: ReactNode }) {
  return <div className="admin-page-head"><div><span className="admin-eyebrow">{eyebrow}</span><h1>{title}</h1><p>{text}</p></div>{action}</div>
}

function MetricCard({ label, value, note, icon, color }: { label: string; value: string | number; note: string; icon: string; color: string }) {
  return <div className={`metric-card metric-card--${color}`}><div className="metric-icon"><Icon name={icon} size={19} /></div><span>{label}</span><strong>{value}</strong><small>{note}</small></div>
}

// ─── ADMIN DASHBOARD ──────────────────────────────────────────────
function AdminDashboard({ onNavigate, user }: { onNavigate: (path: string) => void; user: UserInfo | null }) {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')

  const loadDashboard = () => {
    setLoading(true)
    setLoadError('')
    api.getDashboard()
      .then(res => setData(res))
      .catch(err => setLoadError(err.detail || 'Dashboard data could not be loaded.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadDashboard() }, [])

  if (loading) return <div><p>Loading dashboard metrics from database...</p></div>
  if (loadError) return <div role="alert" className="upload-error">{loadError} <Button variant="outline" onClick={loadDashboard}>Retry</Button></div>

  return <>
    <AdminHeader eyebrow={`Welcome back, ${user ? user.display_name : 'Administrator'}`} title="Dashboard & Analytics" text="Live school activity, announcements, documents, and parent inquiries." action={<Button onClick={() => onNavigate('/admin/notices/new')}><Icon name="plus" size={16} /> Create Notice</Button>} />
    <div className="metric-grid">
      <MetricCard label="Published notices" value={data?.published_notices ?? 0} note="Live on school website" icon="notice" color="blue" />
      <MetricCard label="Draft notices" value={data?.draft_notices ?? 0} note="Unpublished drafts" icon="edit" color="yellow" />
      <MetricCard label="Scheduled notices" value={data?.scheduled_notices ?? 0} note="Queued for future release" icon="calendar" color="green" />
      <MetricCard label="Published resources" value={data?.published_documents ?? 0} note="On the parent resource shelf" icon="file" color="coral" />
    </div>
    <div className="metric-grid" style={{ marginTop: '-10px', marginBottom: '24px' }}>
      <MetricCard label="Total Inquiries" value={data?.total_inquiries ?? 0} note="Contact & admission forms" icon="message" color="blue" />
      <MetricCard label="Unread Inquiries" value={data?.unread_inquiries ?? 0} note="Requires staff review" icon="bell" color="coral" />
    </div>
    <div className="admin-two-col">
      <section className="admin-panel">
        <div className="panel-head"><div><span className="admin-eyebrow">Announcements</span><h2>Recent notices</h2></div><button onClick={() => onNavigate('/admin/notices')}>View all <Icon name="arrow" size={14} /></button></div>
        <div className="recent-list">
          {data?.recent_notices && data.recent_notices.length > 0 ? data.recent_notices.slice(0, 4).map(notice => (
            <button key={notice.id} onClick={() => onNavigate(`/admin/notices/edit/${notice.id}`)}>
              <span className={`recent-icon recent-icon--${notice.category.toLowerCase()}`}><Icon name="notice" size={17} /></span>
              <span><strong>{notice.title}</strong><small>{notice.category} · {notice.status}</small></span>
              <Icon name="chevron" size={16} />
            </button>
          )) : <p className="muted" style={{ padding: '16px' }}>No notices created yet.</p>}
        </div>
      </section>
      <section className="admin-panel quick-panel">
        <div className="panel-head"><div><span className="admin-eyebrow">Action Center</span><h2>Quick actions</h2></div></div>
        <div className="quick-grid">
          <button onClick={() => onNavigate('/admin/notices/new')}><span><Icon name="plus" size={19} /></span><strong>Create notice</strong><small>Post an update</small></button>
          <button onClick={() => onNavigate('/admin/messages')}><span><Icon name="message" size={19} /></span><strong>View messages</strong><small>{data?.unread_inquiries ?? 0} unread enquiries</small></button>
          <button onClick={() => onNavigate('/admin/uploads')}><span><Icon name="upload" size={19} /></span><strong>File manager</strong><small>Upload images & PDFs</small></button>
          <button onClick={() => onNavigate('/admin/uploads')}><span><Icon name="upload" size={19} /></span><strong>Uploads & Resources</strong><small>Manage public files</small></button>
          <button onClick={() => onNavigate('/admin/settings')}><span><Icon name="settings" size={19} /></span><strong>Settings</strong><small>Profile & password</small></button>
          <button onClick={() => onNavigate('/')}><span><Icon name="external" size={19} /></span><strong>Public site</strong><small>View live website</small></button>
        </div>
      </section>
    </div>
  </>
}

// ─── ADMIN MESSAGES / INQUIRIES ───────────────────────────────────
function AdminMessages({ toast }: { toast: (msg: string) => void }) {
  const [inquiries, setInquiries] = useState<ApiInquiry[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [selected, setSelected] = useState<ApiInquiry | null>(null)
  const [page, setPage] = useState(1)
  const pageSize = 10

  const loadData = () => {
    setLoading(true)
    api.getAdminInquiries({ page, page_size: pageSize, search: query || undefined, status_filter: statusFilter })
      .then(res => {
        setInquiries(res.items)
        setTotal(res.total)
      })
      .catch(err => toast(err.detail || 'Failed to load inquiries'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadData()
  }, [query, statusFilter, page])

  const handleStatusChange = async (inquiryId: string, newStatus: string) => {
    try {
      const updated = await api.updateInquiryStatus(inquiryId, newStatus)
      setInquiries(inquiries.map(i => i.id === inquiryId ? updated : i))
      if (selected && selected.id === inquiryId) setSelected(updated)
      toast(`Status updated to ${newStatus}`)
    } catch (err: any) {
      toast(err.detail || 'Could not update status')
    }
  }

  const handleDelete = async (inquiryId: string) => {
    if (!window.confirm('Are you sure you want to delete this enquiry? This action cannot be undone.')) return
    try {
      await api.deleteInquiry(inquiryId)
      setInquiries(inquiries.filter(i => i.id !== inquiryId))
      setTotal(total - 1)
      if (selected && selected.id === inquiryId) setSelected(null)
      toast('Enquiry deleted successfully')
    } catch (err: any) {
      toast(err.detail || 'Could not delete enquiry')
    }
  }

  return <div className="messages-page">
    <AdminHeader eyebrow="Parent Communications" title="Messages & Enquiries" text="Every submission from the website's contact form and admission enquiries is saved here." />
    <div className="admin-toolbar">
      <div className="search-field"><Icon name="search" size={17} /><input value={query} onChange={e => { setQuery(e.target.value); setPage(1) }} placeholder="Search parent name, phone, or email..." /></div>
      <div className="filter-chips">
        {['ALL', 'NEW', 'REVIEWED', 'CONTACTED', 'CLOSED'].map(st => (
          <button key={st} className={statusFilter === st ? 'is-selected' : ''} onClick={() => { setStatusFilter(st); setPage(1) }}>
            {st === 'NEW' ? 'Unread (New)' : st === 'ALL' ? 'All Messages' : st}
          </button>
        ))}
      </div>
    </div>
    <section className="admin-panel table-panel">
      <div className="responsive-table">
        <div className="table-row table-row--head" style={{ gridTemplateColumns: '2fr 1.3fr 1fr 1fr 1.2fr' }}>
          <span>Parent Name</span>
          <span>Contact</span>
          <span>Program / Child</span>
          <span>Status</span>
          <span>Actions</span>
        </div>
        {loading ? <p style={{ padding: '24px' }}>Loading inquiries...</p> : inquiries.length === 0 ? <EmptyState title="No messages found" text="No parent inquiries match your filter or search query." /> : (
          inquiries.map(item => (
            <div key={item.id} className="table-row inquiries-row" style={{ gridTemplateColumns: '2fr 1.3fr 1fr 1fr 1.2fr' }} onClick={() => setSelected(item)}>
              <span className="table-title">
                {item.status === 'NEW' && <span className="unread-dot" title="Unread" />}
                <strong>{item.parent_name}</strong>
              </span>
              <span>
                <small>{item.phone}</small>
                {item.email && <small style={{ display: 'block', color: 'var(--blue)' }}>{item.email}</small>}
              </span>
              <span>
                <span className="table-category">{item.program || 'General'}</span>
                {item.child_age && <small style={{ display: 'block' }}>{item.child_age}</small>}
              </span>
              <span>
                <span className={`status-badge status-badge--${item.status.toLowerCase()}`}>{item.status}</span>
              </span>
              <span className="table-actions" onClick={e => e.stopPropagation()}>
                <button title="View message" onClick={() => setSelected(item)}><Icon name="eye" size={16} /></button>
                <button title="Delete" onClick={() => handleDelete(item.id)}><Icon name="trash" size={16} /></button>
              </span>
            </div>
          ))
        )}
      </div>
    </section>
    {!loading && total > pageSize && <div className="load-more" style={{ display: 'flex', alignItems: 'center', gap: 12 }}><Button variant="outline" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</Button><span>Page {page} of {Math.ceil(total / pageSize)}</span><Button variant="outline" disabled={page >= Math.ceil(total / pageSize)} onClick={() => setPage(page + 1)}>Next</Button></div>}

    {selected && (
      <div className="modal-backdrop" onClick={() => setSelected(null)}>
        <div className="inquiry-detail-modal" onClick={e => e.stopPropagation()}>
          <button className="modal-close" onClick={() => setSelected(null)}><Icon name="close" size={20} /></button>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className={`status-badge status-badge--${selected.status.toLowerCase()}`}>{selected.status}</span>
            <small style={{ color: 'var(--muted)' }}>Received {new Date(selected.created_at).toLocaleString()}</small>
          </div>
          <h2 style={{ margin: '14px 0 4px', fontSize: '26px' }}>{selected.parent_name}</h2>
          <div className="inquiry-meta-grid">
            <div className="inquiry-meta-item"><small>Phone</small><a href={`tel:${selected.phone}`}><strong>{selected.phone}</strong></a></div>
            <div className="inquiry-meta-item"><small>Email</small>{selected.email ? <a href={`mailto:${selected.email}`}><strong>{selected.email}</strong></a> : <strong>Not provided</strong>}</div>
            <div className="inquiry-meta-item"><small>Program of Interest</small><strong>{selected.program || 'General Inquiry'}</strong></div>
            <div className="inquiry-meta-item"><small>Child's Age</small><strong>{selected.child_age || 'Not specified'}</strong></div>
          </div>
          <div className="inquiry-message-box">
            <h4>Parent's Message:</h4>
            <p>{selected.message || 'No message provided.'}</p>
          </div>
          <div className="inquiry-actions-bar">
            <div className="status-toggle-group">
              <small style={{ fontWeight: 800, color: 'var(--muted)' }}>Change status:</small>
              <Button variant="soft" onClick={() => handleStatusChange(selected.id, 'REVIEWED')}>Reviewed</Button>
              <Button variant="soft" onClick={() => handleStatusChange(selected.id, 'CONTACTED')}>Contacted</Button>
              <Button variant="soft" onClick={() => handleStatusChange(selected.id, 'CLOSED')}>Closed</Button>
              {selected.status !== 'NEW' && <Button variant="text" onClick={() => handleStatusChange(selected.id, 'NEW')}>Mark Unread</Button>}
            </div>
            <Button variant="danger" onClick={() => handleDelete(selected.id)}><Icon name="trash" size={15} /> Delete</Button>
          </div>
        </div>
      </div>
    )}
  </div>
}

// ─── ADMIN NOTICES MANAGEMENT ─────────────────────────────────────
function AdminNotices({ onNavigate, toast }: { onNavigate: (path: string) => void; toast: (message: string) => void }) {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('All statuses')
  const [category, setCategory] = useState('')
  const [rows, setRows] = useState<ApiNotice[]>([])
  const [loading, setLoading] = useState(true)

  const loadNotices = () => {
    setLoading(true)
    api.getAdminNotices({ search: query || undefined, category: category || undefined, status: status === 'All statuses' ? undefined : status })
      .then(res => setRows(res.items))
      .catch(err => toast(err.detail || 'Could not load notices'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadNotices()
  }, [query, category, status])

  const handleTogglePublish = async (item: ApiNotice) => {
    const newStatus = item.status === 'PUBLISHED' ? 'UNPUBLISHED' : 'PUBLISHED'
    try {
      await api.updateNotice(item.id, { status: newStatus })
      toast(`Notice status changed to ${newStatus}`)
      loadNotices()
    } catch (err: any) {
      toast(err.detail || 'Failed to update notice')
    }
  }

  const handleDelete = async (noticeId: string) => {
    if (!window.confirm('Are you sure you want to permanently delete this notice?')) return
    try {
      await api.deleteNotice(noticeId)
      toast('Notice deleted')
      loadNotices()
    } catch (err: any) {
      toast(err.detail || 'Failed to delete notice')
    }
  }

  return <>
    <AdminHeader eyebrow="Content Management" title="Notices & Announcements" text="Create, schedule, publish, and manage updates for families." action={<Button onClick={() => onNavigate('/admin/notices/new')}><Icon name="plus" size={16} /> Create Notice</Button>} />
    <div className="admin-toolbar">
      <div className="search-field"><Icon name="search" size={17} /><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search notices by title or excerpt..." /></div>
      <select value={category} onChange={e => setCategory(e.target.value)} aria-label="Filter notices by category"><option value="">All categories</option>{['Important', 'General', 'Events', 'Holidays', 'Documents'].map(value => <option key={value}>{value}</option>)}</select>
      <select value={status} onChange={e => setStatus(e.target.value)}>
        <option>All statuses</option>
        <option>PUBLISHED</option>
        <option>DRAFT</option>
        <option>SCHEDULED</option>
        <option>UNPUBLISHED</option>
        <option>ARCHIVED</option>
      </select>
    </div>
    <section className="admin-panel table-panel">
      <div className="responsive-table">
        <div className="table-row table-row--head"><span>Notice</span><span>Category</span><span>Status</span><span>Created</span><span>Actions</span></div>
        {loading ? <p style={{ padding: '24px' }}>Loading notices...</p> : rows.length === 0 ? <EmptyState title="No notices match" text="Try a different search or status filter." /> : (
          rows.map(item => (
            <div className="table-row" key={item.id}>
              <span className="table-title">
                <span className="table-icon"><Icon name="notice" size={16} /></span>
                <strong>{item.title}</strong>
                {item.is_pinned && <span title="Pinned"><Icon name="pin" size={14} /></span>}
                {item.is_important && <span title="Important" style={{ color: 'var(--yellow)' }}><Icon name="star" size={14} /></span>}
              </span>
              <span><span className="table-category">{item.category}</span></span>
              <span><span className={`table-status table-status--${item.status?.toLowerCase() || 'unknown'}`}>{item.status || 'UNKNOWN'}</span></span>
              <span className="table-muted">{new Date(item.created_at).toLocaleDateString()}</span>
              <span className="table-actions">
                <button aria-label="Preview" title="Public Preview" onClick={() => onNavigate(`/notices/${item.slug || item.id}`)}><Icon name="eye" size={16} /></button>
                <button aria-label="Edit" title="Edit Notice" onClick={() => onNavigate(`/admin/notices/edit/${item.id}`)}><Icon name="edit" size={16} /></button>
                <button aria-label={item.status === 'PUBLISHED' ? 'Unpublish' : 'Publish'} title={item.status === 'PUBLISHED' ? 'Unpublish' : 'Publish'} onClick={() => handleTogglePublish(item)}><Icon name="check" size={16} /></button>
                <button aria-label="Delete" title="Delete Notice" onClick={() => handleDelete(item.id)}><Icon name="trash" size={16} /></button>
              </span>
            </div>
          ))
        )}
      </div>
    </section>
  </>
}

function UploadDropzone({ accept, files, setFiles, label, note, uploadProgress }: { accept: string; files: File[]; setFiles: (files: File[]) => void; label: string; note: string; uploadProgress?: number | null }) {
  const [error, setError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return
    const candidates = Array.from(incoming)
    const acceptedTypes = accept.split(',').map(type => type.trim().toLowerCase()).filter(Boolean)
    const valid = candidates.filter(file => {
      const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
      const typeAllowed = acceptedTypes.some(type => {
        if (type.startsWith('.')) return extension === type
        if (type.endsWith('/*')) return file.type.startsWith(type.slice(0, -1))
        return file.type.toLowerCase() === type
      })
      return typeAllowed && file.size <= 10 * 1024 * 1024
    })
    const invalidCount = candidates.length - valid.length
    setError(invalidCount ? `${invalidCount} file${invalidCount > 1 ? 's were' : ' was'} skipped. Use the listed file types under 10 MB.` : '')
    if (valid.length) setFiles([...files, ...valid])
  }
  const drop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    addFiles(event.dataTransfer.files)
  }
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  return (
    <div className="dropzone" onDragOver={e => e.preventDefault()} onDrop={drop}>
      <input ref={inputRef} className="dropzone-file-input" id={`file-${label}`} type="file" accept={accept} multiple aria-hidden="true" tabIndex={-1} onChange={e => { addFiles(e.currentTarget.files); e.currentTarget.value = '' }} />
      <div className="dropzone-content">
        <span className="dropzone-icon"><Icon name="upload" size={22} /></span>
        <strong>{label}</strong>
        <small>{note}</small>
        <Button variant="soft" type="button" onClick={() => inputRef.current?.click()}>Choose files</Button>
      </div>
      {error && <div className="upload-error" role="alert"><Icon name="info" size={14} />{error}</div>}
      {imageFiles.length > 0 && (
        <div className="upload-preview" aria-label="Selected image previews">
          {imageFiles.map((file, index) => <LocalImagePreview key={`${file.name}-preview-${index}`} file={file} />)}
        </div>
      )}
      {files.length > 0 && (
        <div className="upload-list">
          {files.map((file, index) => (
            <div className="upload-file" key={`${file.name}-${index}`}>
              <FileTypeIcon type={file.type || file.name} />
              <div><strong>{file.name}</strong><small>{(file.size / 1024).toFixed(0)} KB · selected, not uploaded</small></div>
              {uploadProgress != null && <progress className="upload-meter" max={100} value={uploadProgress} aria-label={`Upload progress ${uploadProgress}%`} />}
              <button onClick={() => setFiles(files.filter((_, fileIndex) => fileIndex !== index))} aria-label={`Remove ${file.name}`}><Icon name="close" size={16} /></button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function LocalImagePreview({ file }: { file: File }) {
  const src = useMemo(() => URL.createObjectURL(file), [file])
  useEffect(() => () => URL.revokeObjectURL(src), [src])
  return <img src={src} alt={`Preview of ${file.name}`} />
}

function RichTextToolbar({ onLink }: { onLink: () => void }) {
  const run = (command: string, value?: string) => {
    document.execCommand(command, false, value)
    document.querySelector<HTMLElement>('[contenteditable="true"]')?.focus()
  }
  const buttons = [
    { icon: 'bold', command: 'bold', label: 'Bold' },
    { icon: 'italic', command: 'italic', label: 'Italic' },
    { icon: 'underline', command: 'underline', label: 'Underline' },
    { icon: 'heading', command: 'formatBlock', value: 'h3', label: 'Heading' },
    { icon: 'list', command: 'insertUnorderedList', label: 'Bullet list' },
    { icon: 'list', command: 'insertOrderedList', label: 'Numbered list' },
    { icon: 'link', command: 'link', label: 'Insert link' },
    { icon: 'undo', command: 'undo', label: 'Undo' },
    { icon: 'redo', command: 'redo', label: 'Redo' }
  ]
  return (
    <div className="rich-toolbar">
      {buttons.map(button => (
        <button key={button.label} type="button" title={button.label} aria-label={button.label} onClick={() => button.command === 'link' ? onLink() : run(button.command, button.value)}>
          <Icon name={button.icon} size={16} />
        </button>
      ))}
      <span />
      <button type="button" title="Clear formatting" onClick={() => run('removeFormat')}>
        <Icon name="close" size={15} />
      </button>
    </div>
  )
}

// ─── ADMIN NOTICE COMPOSER ─────────────────────────────────────────
function NoticeComposer({ editId, onNavigate, toast }: { editId?: string; onNavigate: (path: string) => void; toast: (message: string) => void }) {
  const [title, setTitle] = useState('')
  const [excerpt, setExcerpt] = useState('')
  const [category, setCategory] = useState('General')
  const [status, setStatus] = useState('DRAFT')
  const [isPinned, setIsPinned] = useState(false)
  const [isImportant, setIsImportant] = useState(false)
  const [externalUrl, setExternalUrl] = useState('')
  const [publishedAt, setPublishedAt] = useState('')
  const [expiresAt, setExpiresAt] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [uploadedIds, setUploadedIds] = useState<string[]>([])
  const [coverImageId, setCoverImageId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [linkOpen, setLinkOpen] = useState(false)
  const [link, setLink] = useState('')
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewBody, setPreviewBody] = useState('')

  useEffect(() => {
    if (editId) {
      api.getAdminNotice(editId)
        .then(notice => {
          setTitle(notice.title)
          setExcerpt(notice.excerpt)
          setCategory(notice.category)
          setStatus(notice.status || 'DRAFT')
          setIsPinned(notice.is_pinned)
          setIsImportant(notice.is_important)
          setExternalUrl(notice.external_url || '')
          setCoverImageId(notice.cover_image_id || null)
          if (notice.published_at) setPublishedAt(notice.published_at.slice(0, 16))
          if (notice.expires_at) setExpiresAt(notice.expires_at.slice(0, 10))
          const editor = document.querySelector<HTMLElement>('.rich-editor')
          if (editor) editor.innerHTML = notice.body
          if (notice.attachments) setUploadedIds(notice.attachments.map(a => a.file_id))
        })
        .catch(err => toast(err.detail || 'Could not load notice'))
    }
  }, [editId])

  const handleSave = async (targetStatus?: string) => {
    if (!title.trim()) { toast('Please add a notice title.'); return }
    const editor = document.querySelector<HTMLElement>('.rich-editor')
    const bodyHtml = editor ? editor.innerHTML : ''
    if (!bodyHtml.trim()) { toast('Please add notice content.'); return }

    setLoading(true)
    let unlinkedUploadIds: string[] = []
    try {
      let attachmentIds = [...uploadedIds]
      let selectedCoverId = coverImageId
      if (files.length > 0) {
        setUploadProgress(0)
        const uploadRes = await api.uploadFiles(files, setUploadProgress)
        unlinkedUploadIds = uploadRes.files.map(f => f.id)
        attachmentIds = [...attachmentIds, ...unlinkedUploadIds]
        if (!selectedCoverId) selectedCoverId = uploadRes.files.find(f => f.mime_type.startsWith('image/'))?.id || null
      }

      const payload = {
        title: title.trim(),
        excerpt: excerpt.trim() || title.trim(),
        body: bodyHtml,
        category,
        status: targetStatus || status,
        is_pinned: isPinned,
        is_important: isImportant,
        cover_image_id: selectedCoverId,
        external_url: externalUrl.trim() || null,
        attachment_ids: attachmentIds,
        published_at: publishedAt ? new Date(publishedAt).toISOString() : null,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
      }

      if (editId) {
        await api.updateNotice(editId, payload)
        toast('Notice updated successfully!')
      } else {
        await api.createNotice(payload)
        toast('Notice created successfully!')
      }
      onNavigate('/admin/notices')
    } catch (err: any) {
      await Promise.allSettled(unlinkedUploadIds.map(fileId => api.deleteUpload(fileId)))
      toast(err.detail || 'Error saving notice. Please verify all fields.')
    } finally {
      setUploadProgress(null)
      setLoading(false)
    }
  }

  return <>
    <AdminHeader eyebrow="Notice Composer" title={editId ? 'Edit Announcement' : 'Write a New Notice'} text="Compose updates, reminders, and activities for Little Star Playhouse parents." action={<Button variant="outline" onClick={() => onNavigate('/admin/notices')}><Icon name="arrow" size={15} /> Back to Notices</Button>} />
    <div className="composer-grid">
      <section className="admin-panel composer-main">
        <div className="field-group"><label htmlFor="notice-title">Notice Title</label><input id="notice-title" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g., Creative Play Morning Announcement" /></div>
        <div className="field-group"><label htmlFor="notice-excerpt">Short Summary / Excerpt</label><input id="notice-excerpt" value={excerpt} onChange={e => setExcerpt(e.target.value)} placeholder="One or two sentences summarizing the update" /></div>
        <div className="field-grid">
          <label>Category<select value={category} onChange={e => setCategory(e.target.value)}><option>General</option><option>Important</option><option>Events</option><option>Holidays</option><option>Documents</option></select></label>
          <label>External Link (optional)<input value={externalUrl} onChange={e => setExternalUrl(e.target.value)} placeholder="https://example.com" /></label>
        </div>
        <div className="editor-field">
          <div className="editor-label"><label>Notice Body (Rich Text)</label><span>Formatted Content</span></div>
          <RichTextToolbar onLink={() => setLinkOpen(true)} />
          <div className="rich-editor" contentEditable suppressContentEditableWarning role="textbox" aria-label="Notice content editor" aria-multiline="true" onPaste={event => { event.preventDefault(); document.execCommand('insertText', false, event.clipboardData.getData('text/plain')) }}><h3>Welcome families,</h3><p>Write your announcement details here. Keep paragraphs clean and friendly.</p></div>
        </div>
        <div>
          <div className="editor-label"><label>Upload & Attach Files</label><span>{files.length} selected</span></div>
          <UploadDropzone accept=".jpg,.jpeg,.png,.webp,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt" files={files} setFiles={setFiles} label="Drop attachments here" note="Images, PDF, Office, and text files up to 10 MB each. The first uploaded image is used as cover unless set on an existing notice." uploadProgress={uploadProgress} />
        </div>
      </section>
      <aside className="composer-side">
        <section className="admin-panel settings-panel">
          <div className="panel-head"><div><span className="admin-eyebrow">Publication</span><h2>Settings</h2></div></div>
          <label>Status<select value={status} onChange={e => setStatus(e.target.value)}><option value="DRAFT">Draft</option><option value="PUBLISHED">Published</option><option value="SCHEDULED">Scheduled</option><option value="ARCHIVED">Archived</option></select></label>
          <label>Schedule Publication Date & Time<input type="datetime-local" value={publishedAt} onChange={e => setPublishedAt(e.target.value)} /></label>
          <label>Expiry Date (optional)<input type="date" value={expiresAt} onChange={e => setExpiresAt(e.target.value)} /></label>
          <label className="toggle-line"><input type="checkbox" checked={isPinned} onChange={e => setIsPinned(e.target.checked)} /><span className="toggle" />Pin to top of list</label>
          <label className="toggle-line"><input type="checkbox" checked={isImportant} onChange={e => setIsImportant(e.target.checked)} /><span className="toggle" />Mark as Important</label>
          <div className="settings-divider" />
          <div className="editor-actions">
            <Button variant="outline" onClick={() => { setPreviewBody(document.querySelector<HTMLElement>('.rich-editor')?.innerText || ''); setPreviewOpen(true) }}>Preview</Button>
            <Button onClick={() => handleSave('DRAFT')} disabled={loading}>Save Draft</Button>
            <Button variant="soft" onClick={() => handleSave('PUBLISHED')} disabled={loading}>{loading ? 'Saving...' : 'Publish Notice'}</Button>
          </div>
        </section>
      </aside>
    </div>
    {linkOpen && (
      <div className="modal-backdrop">
        <div className="modal-card">
          <button className="modal-close" onClick={() => setLinkOpen(false)}><Icon name="close" size={17} /></button>
          <h2>Insert Link</h2>
          <label>URL<input value={link} onChange={e => setLink(e.target.value)} placeholder="https://" autoFocus /></label>
          <div className="modal-actions">
            <Button variant="outline" onClick={() => setLinkOpen(false)}>Cancel</Button>
            <Button onClick={() => { document.execCommand('createLink', false, link); setLinkOpen(false); toast('Link inserted'); }}>Insert Link</Button>
          </div>
        </div>
      </div>
    )}
    {previewOpen && <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Notice preview" onClick={() => setPreviewOpen(false)}><div className="modal-card" onClick={event => event.stopPropagation()}><button className="modal-close" aria-label="Close preview" onClick={() => setPreviewOpen(false)}><Icon name="close" size={17} /></button><div className="notice-tags"><span className="tag tag--blue">{category}</span>{isImportant && <span className="tag tag--important">Important</span>}</div><h2>{title || 'Notice title preview'}</h2><p className="muted">{excerpt || 'Your notice summary will appear here.'}</p><div className="rich-content" style={{ whiteSpace: 'pre-wrap' }}>{previewBody || 'Your notice content will appear here.'}</div>{externalUrl && <p>External link: {externalUrl}</p>}</div></div>}
  </>
}

// ─── ADMIN UPLOADS MANAGER ─────────────────────────────────────────
function AdminUploads({ toast }: { toast: (msg: string) => void }) {
  const [files, setFiles] = useState<File[]>([])
  const [uploads, setUploads] = useState<UploadedFile[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [search, setSearch] = useState('')
  const [fileType, setFileType] = useState('all')

  const loadUploads = () => {
    setLoading(true)
    api.getAdminUploads({ search: search || undefined, file_type: fileType === 'all' ? undefined : fileType })
      .then(res => setUploads(res.items))
      .catch(err => toast(err.detail || 'Could not load uploads'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadUploads()
  }, [search, fileType])

  const handleUploadSubmit = async () => {
    if (files.length === 0) { toast('Please choose files to upload.'); return }
    setUploading(true)
    try {
      setUploadProgress(0)
      const res = await api.uploadFiles(files, setUploadProgress)
      toast(`Successfully uploaded ${res.files.length} file(s)!`)
      setFiles([])
      loadUploads()
    } catch (err: any) {
      toast(err.detail || 'Upload failed. Ensure files are under 10 MB.')
    } finally {
      setUploadProgress(null)
      setUploading(false)
    }
  }

  const handleCopy = (url: string) => {
    const full = api.absoluteApiUrl(url)
    navigator.clipboard.writeText(full)
    toast('Direct file download URL copied to clipboard!')
  }

  const handleDelete = async (fileId: string) => {
    if (!window.confirm('Delete this file from server storage?')) return
    try {
      await api.deleteUpload(fileId)
      toast('File deleted successfully')
      loadUploads()
    } catch (err: any) {
      toast(err.detail || 'Cannot delete file. It may be in use by a notice or document.')
    }
  }

  return <>
    <AdminHeader eyebrow="File Storage & Public Resources" title="Uploads & Resources" text="Upload general files, publish captioned parent resources, and manage drafts, schedules, and published items from one place." />
    <AdminDocuments toast={toast} embedded />
    <section className="admin-panel" style={{ marginBottom: '24px' }}>
      <div className="panel-head"><div><span className="admin-eyebrow">New Upload</span><h2>Upload Files to Storage</h2></div></div>
      <UploadDropzone accept=".jpg,.jpeg,.png,.webp,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt" files={files} setFiles={setFiles} label="Drop files to upload" note="Images, PDF, Office, and text files up to 10 MB each" uploadProgress={uploadProgress} />
      {files.length > 0 && (
        <div style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
          <Button type="button" onClick={handleUploadSubmit} disabled={uploading}>{uploading ? 'Uploading to Server...' : `Upload ${files.length} File(s) to Storage`} <Icon name="upload" size={15} /></Button>
          <Button type="button" variant="text" onClick={() => setFiles([])}>Clear Selection</Button>
        </div>
      )}
    </section>

    <div className="admin-toolbar">
      <div className="search-field"><Icon name="search" size={17} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search file by name..." /></div>
      <div className="filter-chips">
        {['all', 'image', 'pdf', 'doc'].map(ft => (
          <button key={ft} className={fileType === ft ? 'is-selected' : ''} onClick={() => setFileType(ft)}>
            {ft === 'all' ? 'All Files' : ft.toUpperCase()}
          </button>
        ))}
      </div>
    </div>

    {loading ? <p>Loading storage library...</p> : uploads.length === 0 ? <EmptyState title="No uploaded files" text="Upload files using the drag-and-drop zone above." /> : (
      <div className="upload-manager-grid">
        {uploads.map(file => {
          const isImg = file.mime_type.startsWith('image/')
          return (
            <div key={file.id} className="upload-card">
              <div className="upload-card-thumb">
                {isImg ? <img src={api.absoluteApiUrl(file.download_url)} alt="" /> : <Icon name={file.extension === '.pdf' ? 'pdf' : 'file'} size={36} />}
              </div>
              <div className="upload-card-body">
                <strong title={file.original_filename}>{file.original_filename}</strong>
                <small>{file.extension.toUpperCase()} · {(file.file_size / 1024).toFixed(0)} KB</small>
                {file.created_at && <small style={{ color: '#9aa5b3' }}>{new Date(file.created_at).toLocaleDateString()}</small>}
                <div className="upload-card-actions">
                  <button title="Copy Link" onClick={() => handleCopy(file.download_url)}><Icon name="copy" size={14} /> Copy URL</button>
                  <a href={api.absoluteApiUrl(file.download_url)} target="_blank" rel="noreferrer" title="Open / Preview" style={{ color: 'var(--blue)', fontSize: '11px', fontWeight: 700 }}><Icon name="external" size={14} /></a>
                  <button className="btn-delete" title="Delete" onClick={() => handleDelete(file.id)}><Icon name="trash" size={14} /></button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )}
  </>
}

function AdminGallery({ toast }: { toast: (msg: string) => void }) {
  const [items, setItems] = useState<ApiGalleryItem[]>([])
  const [image, setImage] = useState<File | null>(null)
  const [caption, setCaption] = useState('')
  const [busy, setBusy] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploadError, setUploadError] = useState('')
  const previewUrl = useMemo(() => image ? URL.createObjectURL(image) : '', [image])
  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl) }, [previewUrl])
  const load = () => api.getGallery().then(result => setItems(result.items)).catch(error => toast(error.detail || 'Could not load gallery')).finally(() => setLoading(false))
  useEffect(() => { load() }, [])
  const chooseImage = (file?: File) => {
    if (!file) return
    const supportedName = /\.(jpe?g|png|webp)$/i.test(file.name)
    const supportedMime = !file.type || ['image/jpeg', 'image/png', 'image/webp', 'application/octet-stream'].includes(file.type)
    if (!supportedName || !supportedMime) {
      toast('Choose a JPG, PNG, or WebP image.'); return
    }
    if (file.size > 10 * 1024 * 1024) { toast('Images must be 10 MB or smaller.'); return }
    setUploadError('')
    setImage(file)
  }
  const upload = async () => {
    if (!image || !caption.trim()) { toast('Choose an image and add its caption.'); return }
    setBusy(true)
    try {
      setUploadProgress(0)
      await api.createGalleryImage(image, caption.trim(), setUploadProgress)
      setImage(null); setCaption(''); if (inputRef.current) inputRef.current.value = ''
      toast('Gallery image published.'); await load()
    } catch (error: any) { const message = error.detail || error.message || 'Could not upload gallery image.'; setUploadError(message); toast(message) }
    finally { setUploadProgress(null); setBusy(false) }
  }
  const remove = async (item: ApiGalleryItem) => {
    if (!window.confirm(`Remove “${item.caption}” from the gallery?`)) return
    try { await api.deleteGalleryImage(item.id); toast('Image removed from gallery.'); await load() }
    catch (error: any) { toast(error.detail || 'Could not remove gallery image.') }
  }
  return <>
    <AdminHeader eyebrow="Public photos" title="Gallery" text="Add a photo with a caption. Published images appear in the public gallery." />
    <div className="admin-gallery-layout">
      <section className="admin-panel upload-form">
        <div className="panel-head"><div><span className="admin-eyebrow">New gallery image</span><h2>Share a little moment</h2></div></div>
        <label className="gallery-upload-picker" onDragOver={event => event.preventDefault()} onDrop={event => { event.preventDefault(); chooseImage(event.dataTransfer.files[0]) }}>
          <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp" onChange={event => { chooseImage(event.currentTarget.files?.[0]); event.currentTarget.value = '' }} />
          {image ? <><img src={previewUrl} alt="Selected gallery preview" /><span className="gallery-picker-action">Choose a different image</span></> : <><span className="gallery-picker-icon"><Icon name="image" size={25} /></span><strong>Choose or drop an image</strong><small>JPG, PNG, or WebP · Up to 10 MB</small><span className="gallery-picker-action">Choose image</span></>}
        </label>
        {image && <div className="gallery-selected-name">{image.name}<button type="button" onClick={() => { setImage(null); if (inputRef.current) inputRef.current.value = '' }}>Remove</button></div>}
        <label className="field-group gallery-caption-field">Caption<textarea maxLength={500} rows={3} value={caption} onChange={event => setCaption(event.target.value)} placeholder="Describe this moment" /><small>{caption.length}/500</small></label>
        {uploadError && <div className="upload-error" role="alert"><Icon name="info" size={14} />{uploadError}</div>}
        {uploadProgress != null && <progress className="upload-meter" max={100} value={uploadProgress} aria-label={`Upload progress ${uploadProgress}%`} />}
        <Button onClick={upload} disabled={busy || !image || !caption.trim()}>{busy ? `Uploading ${uploadProgress ?? 0}%…` : 'Upload to Gallery'} <Icon name="upload" size={16} /></Button>
      </section>
      <section className="admin-panel">
        <div className="panel-head"><div><span className="admin-eyebrow">Public gallery</span><h2>Uploaded images</h2></div><span className="panel-count">{items.length} images</span></div>
        {loading ? <p>Loading gallery…</p> : items.length ? <div className="admin-gallery-grid">{items.map(item => <article key={item.id}><img src={api.absoluteApiUrl(item.image_url)} alt={item.caption} /><div><p>{item.caption}</p><button className="btn-delete" aria-label={`Remove ${item.caption}`} onClick={() => remove(item)}><Icon name="trash" size={16} /></button></div></article>)}</div> : <div className="empty-state"><span><Icon name="image" size={25} /></span><h3>No photos yet</h3><p>Upload an image and caption to add the first public gallery item.</p></div>}
      </section>
    </div>
  </>
}

// ─── ADMIN DOCUMENTS ───────────────────────────────────────────────
function AdminDocuments({ toast, embedded = false }: { toast: (message: string) => void; embedded?: boolean }) {
  const [files, setFiles] = useState<File[]>([])
  const [rows, setRows] = useState<ApiDocument[]>([])
  const [title, setTitle] = useState('')
  const [desc, setDesc] = useState('')
  const [category, setCategory] = useState('Forms')
  const [status, setStatus] = useState('PUBLISHED')
  const [publishAt, setPublishAt] = useState('')
  const [expiresAt, setExpiresAt] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)

  const loadDocs = () => {
    api.getAdminDocuments({ page_size: 100 })
      .then(res => setRows(res.items))
      .catch(err => toast(err.detail || 'Could not load documents'))
  }

  useEffect(() => { loadDocs() }, [])

  const handleCreate = async () => {
    if (!title.trim()) { toast('Please provide a document title.'); return }
    if (!editingId && files.length === 0) { toast('Please choose a file to upload for this document.'); return }
    if (files.length > 1) { toast('Choose one file for each document record.'); return }
    if (status === 'SCHEDULED' && !publishAt) { toast('Choose a publication date and time for scheduled documents.'); return }

    setLoading(true)
    let unlinkedUploadId: string | null = null
    try {
      if (files.length) setUploadProgress(0)
      const uploadRes = files.length ? await api.uploadFiles(files, setUploadProgress) : null
      unlinkedUploadId = uploadRes?.files[0]?.id || null
      const payload = {
        title: title.trim(), description: desc.trim(), category, status,
        ...(uploadRes ? { file_id: uploadRes.files[0].id } : {}),
        published_at: publishAt ? new Date(publishAt).toISOString() : null,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
      }
      if (editingId) await api.updateDocument(editingId, payload)
      else await api.createDocument({ ...payload, file_id: uploadRes!.files[0].id })
      toast(editingId ? 'Document updated successfully!' : 'Document created successfully!')
      setTitle('')
      setDesc('')
      setFiles([])
      setEditingId(null)
      loadDocs()
    } catch (err: any) {
      if (unlinkedUploadId) await api.deleteUpload(unlinkedUploadId).catch(() => {})
      toast(err.detail || 'Failed to create document.')
    } finally {
      setUploadProgress(null)
      setLoading(false)
    }
  }

  const handleToggleStatus = async (doc: ApiDocument) => {
    const newStatus = doc.status === 'PUBLISHED' ? 'DRAFT' : 'PUBLISHED'
    try {
      await api.updateDocument(doc.id, { status: newStatus })
      toast(`Document status set to ${newStatus}`)
      loadDocs()
    } catch (err: any) {
      toast(err.detail || 'Could not update document')
    }
  }

  const handleDelete = async (docId: string) => {
    if (!window.confirm('Delete this document entry?')) return
    try {
      await api.deleteDocument(docId)
      toast('Document removed')
      loadDocs()
    } catch (err: any) {
      toast(err.detail || 'Could not delete document')
    }
  }

  return <>
    {embedded ? <div className="uploads-resources-heading"><span className="admin-eyebrow">Public Website Resources</span><h2>Manage uploads shown on the website</h2><p>Add a file with a caption, then publish it now, save it as a draft, or schedule it for later.</p></div> : <AdminHeader eyebrow="Parent Resource Shelf" title="Uploads & Documents" text="Manage school forms, parent guidelines, circulars, and activity sheets." />}
    <div className="upload-layout">
      <section className="admin-panel upload-form">
        <div className="panel-head"><div><span className="admin-eyebrow">New Document</span><h2>Add a Resource</h2></div></div>
        <div className="field-group"><label>Document Title</label><input value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g., Parent Welcome Guide 2026" /></div>
        <div className="field-group"><label>Description</label><textarea rows={3} value={desc} onChange={e => setDesc(e.target.value)} placeholder="Help families understand what this resource is for." /></div>
        <div className="field-grid">
          <label>Category<select value={category} onChange={e => setCategory(e.target.value)}><option>Forms</option><option>School Circulars</option><option>Parent Guidelines</option><option>Event Documents</option><option>Learning Resources</option><option>Other Documents</option></select></label>
          <label>Publication Status<select value={status} onChange={e => setStatus(e.target.value)}><option value="DRAFT">Draft</option><option value="SCHEDULED">Scheduled</option><option value="PUBLISHED">Published</option><option value="UNPUBLISHED">Unpublished</option><option value="ARCHIVED">Archived</option></select></label>
        </div>
        <div className="field-grid"><label>Publish date & time<input type="datetime-local" value={publishAt} onChange={e => setPublishAt(e.target.value)} /></label><label>Expiry date<input type="date" value={expiresAt} onChange={e => setExpiresAt(e.target.value)} /></label></div>
        <UploadDropzone accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.webp" files={files} setFiles={setFiles} label="Select Document File" note="Drag and drop or browse · PDF, Office, text, and image formats (Max 10 MB)" uploadProgress={uploadProgress} />
        <div className="editor-actions">
          <Button onClick={handleCreate} disabled={loading}>{loading ? 'Saving...' : editingId ? 'Save Document Changes' : 'Save Document'} <Icon name="arrow" size={15} /></Button>
          <Button variant="text" onClick={() => { setTitle(''); setDesc(''); setFiles([]); setEditingId(null); setPublishAt(''); setExpiresAt(''); }}>Clear</Button>
        </div>
      </section>
      <section className="admin-panel">
        <div className="panel-head"><div><span className="admin-eyebrow">Current Library</span><h2>Resource Records</h2></div><span className="panel-count">{rows.length} records</span></div>
        <div className="resource-admin-list">
          {rows.length === 0 ? <p className="muted" style={{ padding: '20px' }}>No documents in repository.</p> : rows.map(doc => (
            <div key={doc.id} className="resource-admin-row">
              <FileTypeIcon type={doc.file?.extension || 'PDF'} />
              <div><strong>{doc.title}</strong><small>{doc.category} · {(doc.file?.file_size ? (doc.file.file_size / 1024).toFixed(0) : '0')} KB</small></div>
              <span className={`table-status table-status--${doc.status.toLowerCase()}`}>{doc.status}</span>
              <div className="table-actions">
                <button title="Edit document" onClick={() => { setEditingId(doc.id); setTitle(doc.title); setDesc(doc.description); setCategory(doc.category); setStatus(doc.status); setPublishAt(doc.published_at ? doc.published_at.slice(0, 16) : ''); setExpiresAt(doc.expires_at ? doc.expires_at.slice(0, 10) : ''); window.scrollTo({ top: 0, behavior: 'smooth' }) }}><Icon name="edit" size={16} /></button>
                <a href={api.absoluteApiUrl(doc.download_url)} target="_blank" rel="noreferrer" title="View / Download" className="button button--small button--text"><Icon name="download" size={16} /></a>
                <button title={doc.status === 'PUBLISHED' ? 'Unpublish' : 'Publish'} onClick={() => handleToggleStatus(doc)}><Icon name="check" size={16} /></button>
                <button title="Delete" onClick={() => handleDelete(doc.id)}><Icon name="trash" size={16} /></button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  </>
}

// ─── ADMIN SETTINGS ────────────────────────────────────────────────
function AdminSettings({ user, onLogout, toast }: { user: UserInfo | null; onLogout: () => void; toast: (msg: string) => void }) {
  const [currentPwd, setCurrentPwd] = useState('')
  const [newPwd, setNewPwd] = useState('')
  const [confirmPwd, setConfirmPwd] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPwd.length < 12) { toast('New password must be at least 12 characters.'); return }
    if (newPwd !== confirmPwd) { toast('New passwords do not match.'); return }

    setLoading(true)
    try {
      await api.changePassword(currentPwd, newPwd)
      toast('Password successfully updated! Use your new password on next sign-in.')
      setCurrentPwd('')
      setNewPwd('')
      setConfirmPwd('')
    } catch (err: any) {
      toast(err.detail || 'Could not change password. Verify your current password.')
    } finally {
      setLoading(false)
    }
  }

  return <>
    <AdminHeader eyebrow="Administration" title="Settings & Profile" text="Manage administrator credentials, view security settings, and update system parameters." />
    <div className="settings-grid-layout">
      <section className="admin-panel">
        <div className="panel-head"><div><span className="admin-eyebrow">Account Details</span><h2>Administrator Profile</h2></div></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '16px', background: 'var(--yellow)', display: 'grid', placeItems: 'center', color: '#8b6500', fontSize: '20px', fontWeight: 900 }}>
            {user ? user.display_name.slice(0, 2).toUpperCase() : 'LS'}
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '20px' }}>{user?.display_name || 'Administrator'}</h3>
            <span style={{ fontSize: '13px', color: 'var(--muted)' }}>{user?.username}</span>
            <span className="table-category" style={{ marginLeft: '8px' }}>{user?.role || 'ADMIN'}</span>
          </div>
        </div>
        <div style={{ marginTop: '20px' }}>
          <Button variant="danger" onClick={onLogout}><Icon name="logout" size={16} /> Sign Out of All Tabs</Button>
        </div>
      </section>

      <section className="admin-panel">
        <div className="panel-head"><div><span className="admin-eyebrow">Security</span><h2>Change Password</h2></div></div>
        <form className="password-change-form" onSubmit={handlePasswordChange}>
          <label>Current Password<input className="password-change-input" type="password" required value={currentPwd} onChange={e => setCurrentPwd(e.target.value)} placeholder="Enter current password" /></label>
          <label>New Password<div className="password-change-input-wrap"><input className="password-change-input" type={showPwd ? 'text' : 'password'} required minLength={12} value={newPwd} onChange={e => setNewPwd(e.target.value)} placeholder="Minimum 12 characters" /><button type="button" className="toggle-pwd-btn" aria-label={showPwd ? 'Hide new password' : 'Show new password'} onClick={() => setShowPwd(!showPwd)}><Icon name={showPwd ? 'eyeOff' : 'eye'} size={18} /></button></div></label>
          <label>Confirm New Password<input className="password-change-input" type="password" required value={confirmPwd} onChange={e => setConfirmPwd(e.target.value)} placeholder="Repeat new password" /></label>
          <Button type="submit" disabled={loading} className="password-change-submit">{loading ? 'Updating Password...' : 'Update Password'} <Icon name="lock" size={16} /></Button>
        </form>
      </section>
    </div>
  </>
}

// ─── ADMIN MAIN CONTAINER ──────────────────────────────────────────
function AdminPage({ path, onNavigate }: { path: string; onNavigate: (path: string) => void }) {
  const [currentUser, setCurrentUser] = useState<UserInfo | null>(null)
  const [authChecking, setAuthChecking] = useState(true)
  const [toastText, setToastText] = useState('')
  const [unreadCount, setUnreadCount] = useState(0)

  // Verify authentication on mount
  useEffect(() => {
    api.getMe()
      .then(res => {
        setCurrentUser(res.user)
        // Refresh unread inquiry counts
        api.getDashboard().then(d => setUnreadCount(d.unread_inquiries)).catch(() => {})
      })
      .catch(() => {
        setCurrentUser(null)
      })
      .finally(() => setAuthChecking(false))
  }, [path])

  const handleLogout = async () => {
    try {
      await api.logout()
    } catch {}
    setCurrentUser(null)
    onNavigate('/admin')
  }

  const toast = (message: string) => setToastText(message)

  if (authChecking) {
    return <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: 'var(--warm)' }}>
      <p style={{ fontWeight: 800, color: 'var(--muted)' }}><Icon name="sparkle" size={20} /> Checking administrator credentials...</p>
    </div>
  }

  // Not logged in -> Show login card
  if (!currentUser) {
    return <AdminLogin onLoginSuccess={user => {
      setCurrentUser(user)
      onNavigate(path === '/admin' ? '/admin/dashboard' : path)
    }} onNavigate={onNavigate} />
  }

  // Logged in: resolve route
  let content: ReactNode
  if (path === '/admin' || path === '/admin/dashboard') {
    content = <AdminDashboard onNavigate={onNavigate} user={currentUser} />
  } else if (path === '/admin/messages') {
    content = <AdminMessages toast={toast} />
  } else if (path === '/admin/notices') {
    content = <AdminNotices onNavigate={onNavigate} toast={toast} />
  } else if (path === '/admin/notices/new') {
    content = <NoticeComposer onNavigate={onNavigate} toast={toast} />
  } else if (path.startsWith('/admin/notices/edit/')) {
    const editId = path.split('/')[4]
    content = <NoticeComposer editId={editId} onNavigate={onNavigate} toast={toast} />
  } else if (path === '/admin/uploads' || path === '/admin/documents') {
    content = <AdminUploads toast={toast} />
  } else if (path === '/admin/gallery') {
    content = <AdminGallery toast={toast} />
  } else if (path === '/admin/settings') {
    content = <AdminSettings user={currentUser} onLogout={handleLogout} toast={toast} />
  } else {
    content = <AdminDashboard onNavigate={onNavigate} user={currentUser} />
  }

  return (
    <AdminLayout path={path === '/admin/documents' ? '/admin/uploads' : path} onNavigate={onNavigate} user={currentUser} onLogout={handleLogout} unreadCount={unreadCount}>
      {content}
      {toastText && <Toast message={toastText} onClose={() => setToastText('')} />}
    </AdminLayout>
  )
}

// ─── ROOT APPLICATION COMPONENT ────────────────────────────────────
export default function App() {
  const [path, setPath] = useState(window.location.pathname || '/')
  const [lang, setLang] = useState<Lang>('en')

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname)
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  const navigate = (nextPath: string) => {
    const target = nextPath.startsWith('/') ? nextPath : `/${nextPath}`
    window.history.pushState({}, '', target)
    setPath(target)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (path.startsWith('/admin')) return <AdminPage path={path} onNavigate={navigate} />
  if (path.startsWith('/notices/')) return <NoticeDetailPage id={path.split('/')[2]} lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/notices') return <NoticesPage lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/documents') return <DocumentsPage lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/about') return <AboutPage lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/programs') return <ProgramsPage lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/our-little-world') return <WorldPage lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/gallery') return <GalleryPage lang={lang} setLang={setLang} onNavigate={navigate} />
  if (path === '/contact') return <ContactPage lang={lang} setLang={setLang} onNavigate={navigate} />
  return <HomePage lang={lang} setLang={setLang} onNavigate={navigate} />
}
