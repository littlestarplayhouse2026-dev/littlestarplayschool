/** Public site contact links are supplied at build time through Vite env vars. */
const env = import.meta.env

export const siteConfig = {
  phoneDisplay: env.VITE_PUBLIC_PHONE_DISPLAY?.trim() || '',
  phoneLink: env.VITE_PUBLIC_PHONE_LINK?.trim() || '',
  email: env.VITE_PUBLIC_EMAIL?.trim() || '',
  emailLink: env.VITE_PUBLIC_EMAIL_LINK?.trim() || '',
  whatsappUrl: env.VITE_PUBLIC_WHATSAPP_URL?.trim() || '',
  mapsUrl: env.VITE_PUBLIC_MAPS_URL?.trim() || '',
}
