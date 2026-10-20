export type Category = 'Important' | 'General' | 'Events' | 'Holidays' | 'Documents'
export type NoticeStatus = 'Published' | 'Draft' | 'Scheduled'
export type DocumentCategory = 'Forms' | 'School Circulars' | 'Parent Guidelines' | 'Event Documents' | 'Learning Resources' | 'Other Documents'

export type Notice = {
  id: string
  title: string
  category: Category
  date: string
  author: string
  excerpt: string
  body: string[]
  important?: boolean
  pinned?: boolean
  status: NoticeStatus
  cover?: string
  attachments?: { name: string; type: 'pdf' | 'doc' | 'image'; size: string }[]
}

export type DocRecord = {
  id: string
  title: string
  description: string
  category: DocumentCategory
  type: 'PDF' | 'DOCX' | 'JPG'
  size: string
  date: string
  status: 'Published' | 'Draft'
}

export const notices: Notice[] = [
  {
    id: 'welcome-circle', title: 'Important School Announcement', category: 'Important', date: 'Oct 18, 2026', author: 'Little Star Playhouse', important: true, pinned: true, status: 'Published', cover: '/assets/gallery-classroom.webp',
    excerpt: 'A gentle reminder for families about our welcome circle and the little routines that help each child settle into play.',
    body: ['Our welcome circle is a calm, happy start to the day. Children are invited to arrive with a little time for greetings, putting belongings away, and choosing their first play invitation.', 'Families can use this notice as a conversation starter at home. We will keep sharing small, helpful updates as the term unfolds.'],
    attachments: [{ name: 'Parent welcome note.pdf', type: 'pdf', size: '820 KB' }]
  },
  {
    id: 'colour-day', title: 'Upcoming School Activity', category: 'Events', date: 'Oct 14, 2026', author: 'Little Star Playhouse', status: 'Published', cover: '/assets/notice-classroom.webp',
    excerpt: 'We are making room for colour, texture, music, and movement in a special creative play morning.',
    body: ['Our upcoming creative play morning will bring together painting, building, music, and movement. Children can explore at their own pace with caring guidance from the playhouse team.', 'Please check the family noticeboard for the latest timing details and any items that may be helpful to bring.'],
    attachments: [{ name: 'Creative play guide.pdf', type: 'pdf', size: '1.2 MB' }, { name: 'Colour day preview.jpg', type: 'image', size: '460 KB' }]
  },
  {
    id: 'parent-question', title: 'Information for Parents', category: 'General', date: 'Oct 09, 2026', author: 'Little Star Playhouse', status: 'Published',
    excerpt: 'A friendly guide to the questions families often ask when they first visit our little world of learning.',
    body: ['Every child arrives with their own rhythm. We are always happy to answer questions about our programs, daily flow, and how to begin an admission enquiry.', 'If you would like a conversation, please call the school or send a WhatsApp message so we can find a helpful time.'],
    attachments: [{ name: 'Parent questions.docx', type: 'doc', size: '58 KB' }]
  },
  {
    id: 'learning-resources', title: 'New Learning Resources Available', category: 'Documents', date: 'Oct 02, 2026', author: 'Little Star Playhouse', status: 'Draft',
    excerpt: 'Browse the growing parent resource shelf for gentle ideas, printable prompts, and school circulars.',
    body: ['This is a preview notice for the prototype resource shelf. In Phase 2, resources will be connected to real document records and storage.', 'For now, explore the sample library to see how a parent-friendly download experience could work.'],
    attachments: [{ name: 'Learning shelf preview.pdf', type: 'pdf', size: '940 KB' }]
  }
]

export const documents: DocRecord[] = [
  { id: 'admission-enquiry', title: 'Admission Enquiry Form', description: 'A simple starting point for families who would like to ask about joining the playhouse.', category: 'Forms', type: 'PDF', size: '420 KB', date: 'Oct 18, 2026', status: 'Published' },
  { id: 'welcome-guide', title: 'Parent Welcome Guide', description: 'A warm introduction to Little Star Playhouse and the little routines that shape each day.', category: 'Parent Guidelines', type: 'PDF', size: '1.1 MB', date: 'Oct 12, 2026', status: 'Published' },
  { id: 'creative-play', title: 'Creative Play Activity Sheet', description: 'Ideas for colour, texture, building, and storytelling at home.', category: 'Learning Resources', type: 'JPG', size: '760 KB', date: 'Oct 08, 2026', status: 'Published' },
  { id: 'holiday-note', title: 'Holiday Information Circular', description: 'A prototype school circular showing the document library pattern.', category: 'School Circulars', type: 'DOCX', size: '85 KB', date: 'Sep 28, 2026', status: 'Draft' },
  { id: 'music-morning', title: 'Music Morning Activity Note', description: 'A preview event document for singing, dancing, and movement.', category: 'Event Documents', type: 'PDF', size: '690 KB', date: 'Sep 21, 2026', status: 'Published' }
]

export const programs = [
  { title: 'Playgroup', age: 'Ages 2–3', text: 'A gentle first step into shared play, stories, songs, and confident little routines.', color: 'yellow', icon: 'star', image: '/assets/playgroup.webp' },
  { title: 'Nursery Readiness', age: 'Ages 3–4', text: 'Growing language, curiosity, independence, and the joy of learning together.', color: 'blue', icon: 'book', image: '/assets/nursery-readiness.webp' },
  { title: 'Creative Play', age: 'Ages 3–5', text: 'Open-ended making, movement, music, and discovery for expressive young minds.', color: 'green', icon: 'brush', image: '/assets/creative-play.webp' }
]

export const activities = [
  { title: 'Storytime', text: 'Little ears, big imaginations.', color: 'coral', icon: 'book', wide: true },
  { title: 'Creative art', text: 'Colour is a language all its own.', color: 'yellow', icon: 'brush' },
  { title: 'Building & discovery', text: 'Try, stack, tumble, try again.', color: 'blue', icon: 'blocks' },
  { title: 'Music & singing', text: 'Every voice belongs in the chorus.', color: 'green', icon: 'music' },
  { title: 'Dancing & movement', text: 'Make space for happy feet.', color: 'orange', icon: 'sparkle', wide: true }
]

export const faq = [
  { q: 'What age group is Little Star Playhouse for?', a: 'Our programs are designed for young learners in the early childhood years. Please contact the school to talk through the best starting point for your child.' },
  { q: 'What programs can families ask about?', a: 'Families can ask about Playgroup, Nursery Readiness, and Creative Play. The team can share the current rhythm and availability during an enquiry.' },
  { q: 'How do I make an admission enquiry?', a: 'Use the admission buttons on this website to call, email, or message the playhouse.' },
  { q: 'Where is the playhouse located?', a: 'Little Star Playhouse is in Ward 4, Janakpurdham, Dhanusha, Nepal, near the old Sanchaykosh Office on the way to Kataiyachauri.' },
  { q: 'How can I confirm fees and schedules?', a: 'Please contact the school directly so the team can share the latest information for your family. This prototype does not invent fee or schedule details.' }
]

export const translations = {
  en: {
    nav: { home: 'Home', about: 'About Us', programs: 'Programs', world: 'Our Little World', notices: 'Notices', documents: 'Uploads', gallery: 'Gallery', contact: 'Contact', admin: 'Admin Preview' },
    actions: { join: "Let's Join the Fun!", headerEnquire: 'Enquire', enquire: 'Enquire About Admission', discover: 'Discover Our Playhouse', explore: 'Explore the little world', learnMore: 'Learn more', readNotice: 'Read Full Notice', download: 'Download', view: 'View', call: 'Call the school', whatsapp: 'Enquire on WhatsApp', directions: 'Get directions', email: 'Send an email' },
    labels: { mock: 'Development preview • Mock content', search: 'Search', all: 'All', important: 'Important', general: 'General Announcements', events: 'Events', holidays: 'Holidays', docs: 'Documents', newest: 'Newest first', noResults: 'No little notes found', noResultsText: 'Try a different search or filter and we will look again.', prototype: 'Prototype only — changes are not saved after refresh.', localOnly: 'Files stay in this browser preview and are not uploaded to permanent storage.' }
  },
  ne: {
    nav: { home: 'गृहपृष्ठ', about: 'हाम्रो बारेमा', programs: 'कार्यक्रमहरू', world: 'हाम्रो सानो संसार', notices: 'सूचनाहरू', documents: 'अपलोडहरू', gallery: 'ग्यालरी', contact: 'सम्पर्क', admin: 'एडमिन प्रिभ्यू' },
    actions: { join: 'रमाइलोमा जोडिनुहोस्!', headerEnquire: 'सोधपुछ', enquire: 'भर्नाबारे सोध्नुहोस्', discover: 'हाम्रो प्लेहाउस हेर्नुहोस्', explore: 'सानो संसार अन्वेषण गर्नुहोस्', learnMore: 'थप जान्नुहोस्', readNotice: 'पूरा सूचना पढ्नुहोस्', download: 'डाउनलोड', view: 'हेर्नुहोस्', call: 'स्कुलमा फोन गर्नुहोस्', whatsapp: 'WhatsApp मा सोध्नुहोस्', directions: 'दिशा हेर्नुहोस्', email: 'इमेल पठाउनुहोस्' },
    labels: { mock: 'विकास प्रिभ्यू • नमूना सामग्री', search: 'खोज्नुहोस्', all: 'सबै', important: 'महत्त्वपूर्ण', general: 'सामान्य सूचना', events: 'कार्यक्रमहरू', holidays: 'बिदाहरू', docs: 'कागजातहरू', newest: 'नयाँ पहिले', noResults: 'कुनै सूचना भेटिएन', noResultsText: 'अर्को खोज वा फिल्टर प्रयास गर्नुहोस्।', prototype: 'प्रोटोटाइप मात्र — रिफ्रेसपछि परिवर्तनहरू सुरक्षित हुँदैनन्।', localOnly: 'फाइलहरू यही ब्राउजर प्रिभ्यूमा रहन्छन्, स्थायी भण्डारणमा अपलोड हुँदैनन्।' }
  }
} as const

export type Lang = keyof typeof translations
