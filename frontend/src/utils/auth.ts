import { errorMap } from "@/lib/firebase";

/**
 * Handle authentication errors with Firebase error messages
 */
export const handleAuthError = (error: any) => {
  if (errorMap[error.code]) {
    throw new Error(errorMap[error.code]);
  }
  throw error;
};
