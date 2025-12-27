import { create } from "zustand";
import { persist } from "zustand/middleware";

interface NotificationState {
  provider: "discord_webhook" | "telegram_bot" | "slack_webhook" | "custom";
  credentials: Record<string, any>;
  setProvider: (
    provider: "discord_webhook" | "telegram_bot" | "slack_webhook" | "custom"
  ) => void;
  setCredentials: (credentials: Record<string, any>) => void;
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set) => ({
      provider: "discord_webhook",
      credentials: {},
      setProvider: (provider) => set({ provider }),
      setCredentials: (credentials) => set({ credentials }),
    }),
    {
      name: "notification-storage",
    }
  )
);
