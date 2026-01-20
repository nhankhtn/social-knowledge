import { useEffect } from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { signInWithPopup, GoogleAuthProvider, signOut } from "firebase/auth";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/firebase";
import { useAuthStore } from "@/store/authStore";
import { paths } from "@/paths";
import { useLogin } from "./useUser";
import { handleAuthError } from "@/utils/auth";
import { trackLogin, trackLogout, setAnalyticsUserId, setAnalyticsUserProperties } from "@/lib/analytics";

export const useAuth = () => {
  const [user, loading, error] = useAuthState(auth);
  const { setUser, setLoading, logout: logoutStore } = useAuthStore();
  const router = useRouter();
  const loginMutation = useLogin();

  useEffect(() => {
    setUser(user || null);
    setLoading(loading);

    // Set analytics user ID and properties when user changes
    if (user) {
      setAnalyticsUserId(user.uid);
      setAnalyticsUserProperties({
        email: user.email || undefined,
        display_name: user.displayName || undefined,
      });
    } else {
      setAnalyticsUserId(null);
    }
  }, [user, loading]);

  const loginWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken();

      // Store token
      if (typeof window !== "undefined") {
        localStorage.setItem("auth_token", token);
      }

      // Call backend API to save user - REQUIRED
      try {
        await loginMutation.mutateAsync({
          firebase_token: token,
          email: result.user.email || "",
          display_name: result.user.displayName || undefined,
          photo_url: result.user.photoURL || undefined,
        });

        console.log("User logged in successfully");
        trackLogin("google");
        return result.user;
      } catch (apiError: any) {
        // Sign out from Firebase since backend registration failed
        await signOut(auth);
        handleAuthError(apiError);
      }
    } catch (error: any) {
      handleAuthError(error);
    }
  };

  const logout = async () => {
    try {
      trackLogout();
      await signOut(auth);
      logoutStore();
      router.push(paths.login);
    } catch (error) {
      handleAuthError(error);
      console.error("Logout error:", error);
    }
  };

  return {
    user,
    loading,
    error,
    loginWithGoogle,
    logout,
  };
};
