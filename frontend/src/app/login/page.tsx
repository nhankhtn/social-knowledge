"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import LoginForm from "@/app/login/_sections/LoginForm";
import { paths } from "@/paths";
import { useAuth } from "@/hooks/useAuth";
import { usePageTracking } from "@/hooks/usePageTracking";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  usePageTracking();

  useEffect(() => {
    if (!loading && user) {
      router.push(paths.home);
    }
  }, [user, loading]);

  if (loading) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900'></div>
      </div>
    );
  }

  return <LoginForm />;
}
