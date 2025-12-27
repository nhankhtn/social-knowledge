"use client";

import { useAuth } from "@/hooks/useAuth";
import { useNotificationStore } from "@/store/notificationStore";
import NotificationForm from "@/app/_sections/NotificationForm";
import { LogOut, Settings, Bell } from "lucide-react";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const { credentials } = useNotificationStore();

  return (
    <div className='min-h-screen bg-gray-50'>
      {/* Header */}
      <header className='bg-white shadow-sm border-b'>
        <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex justify-between items-center h-16'>
            <div className='flex items-center gap-2'>
              <Bell className='w-6 h-6 text-indigo-600' />
              <h1 className='text-xl font-semibold text-gray-900'>
                Social Knowledge
              </h1>
            </div>
            <div className='flex items-center gap-4'>
              {user && (
                <div className='flex items-center gap-3'>
                  <img
                    src={user.photoURL || ""}
                    alt={user.displayName || ""}
                    className='w-8 h-8 rounded-full'
                  />
                  <span className='text-sm text-gray-700'>
                    {user.displayName}
                  </span>
                </div>
              )}
              <button
                onClick={logout}
                className='flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors'
              >
                <LogOut className='w-4 h-4' />
                Đăng xuất
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'>
        <div className='mb-8'>
          <h2 className='text-2xl font-bold text-gray-900 mb-2'>
            Cài đặt Thông báo
          </h2>
          <p className='text-gray-600'>
            Cấu hình kênh thông báo để nhận tin tức tự động
          </p>
        </div>

        <NotificationForm />

        {credentials && Object.keys(credentials).length > 0 && (
          <div className='mt-8 bg-green-50 border border-green-200 rounded-lg p-4'>
            <div className='flex items-center gap-2'>
              <div className='w-2 h-2 bg-green-500 rounded-full animate-pulse'></div>
              <span className='text-sm text-green-800 font-medium'>
                Kênh thông báo đã được cấu hình
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
