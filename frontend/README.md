# Social Knowledge Frontend

Frontend application built with Next.js, Firebase Auth, React Query, Zustand, and Axios.

## Features

- 🔐 Google Authentication với Firebase
- 📡 Quản lý Webhook URL (Discord/Custom)
- 🎨 Modern UI với Tailwind CSS
- ⚡ React Query cho data fetching
- 🗄️ Zustand cho state management
- 📦 Axios cho API calls

## Setup

1. **Cài đặt dependencies:**
```bash
npm install
```

2. **Cấu hình Firebase:**
   - Tạo project trên [Firebase Console](https://console.firebase.google.com/)
   - Enable Google Authentication
   - Copy config vào `.env.local`

3. **Tạo file `.env.local`:**
```bash
cp .env.local.example .env.local
```

4. **Điền thông tin Firebase:**
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

Mở [http://localhost:3000](http://localhost:3000) trong browser.

## Build

```bash
npm run build
npm start
```

## Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Firebase Auth** - Authentication
- **React Query** - Data fetching & caching
- **Zustand** - State management
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Project Structure

```
frontend/
├── app/              # Next.js app directory
│   ├── layout.tsx    # Root layout
│   ├── page.tsx      # Home page
│   └── login/        # Login page
├── src/
│   ├── components/    # React components
│   │   ├── Dashboard.tsx
│   │   ├── LoginForm.tsx
│   │   └── WebhookForm.tsx
│   ├── hooks/        # Custom hooks
│   │   └── useAuth.ts
│   ├── lib/          # Utilities
│   │   ├── firebase.ts
│   │   └── api.ts
│   └── store/        # Zustand stores
│       ├── authStore.ts
│       └── webhookStore.ts
```

