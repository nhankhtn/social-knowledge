"use client";

import { initializeFirebase } from "@/lib/firebase";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function AuthInitializer({ children }: { children: React.ReactNode }) {
  // Initialize auth state
  useAuth();
  return <>{children}</>;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [isFirebaseInitialized, setIsFirebaseInitialized] = useState(false);

  const queryClient = useMemo(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      }),
    []
  );

  useEffect(() => {
    const init = async () => {
      try {
        await initializeFirebase();
        console.log("[initializeFirebase] success");
      } catch (error) {
        console.error("[initializeFirebase] error", error);
      }
      setIsFirebaseInitialized(true);
    };

    init();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ToastContainer
        position='top-right'
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme='light'
      />{" "}
      {isFirebaseInitialized ? (
        <AuthInitializer>{children}</AuthInitializer>
      ) : (
        <div className='flex items-center justify-center min-h-screen'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900'></div>
        </div>
      )}
    </QueryClientProvider>
  );
}
