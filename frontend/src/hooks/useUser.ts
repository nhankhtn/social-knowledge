import { useMutation, useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

interface User {
  id: number;
  firebase_uid: string;
  email: string;
  display_name?: string;
  photo_url?: string;
  role: string;
  created_at: string;
  updated_at: string;
  last_login_at?: string;
}

interface LoginData {
  firebase_token: string;
  email: string;
  display_name?: string;
  photo_url?: string;
}

interface UpdateUserData {
  display_name?: string;
  photo_url?: string;
}

interface NotificationChannel {
  id: number;
  user_id: number;
  provider: string;
  credentials: Record<string, any>;
  name?: string;
  is_active: boolean;
  notification_hours?: number[];
  created_at: string;
  updated_at: string;
}

interface CreateNotificationChannelData {
  provider: string;
  credentials: Record<string, any>;
  name?: string;
  notification_hours?: number[];
}

interface UpdateNotificationChannelData {
  provider?: string;
  credentials?: Record<string, any>;
  name?: string;
  is_active?: boolean;
  notification_hours?: number[];
}

export const useLogin = () => {
  return useMutation({
    mutationFn: async (data: LoginData) => {
      const response = await api.post<User>("/auth/login", data);
      return response.data;
    },
  });
};

export const useGetUser = () => {
  return useQuery({
    queryKey: ["user"],
    queryFn: async () => {
      const response = await api.get<User>("/auth/me");
      return response.data;
    },
  });
};

export const useUpdateUser = () => {
  return useMutation({
    mutationFn: async (data: UpdateUserData) => {
      const response = await api.put<User>("/auth/me", data);
      return response.data;
    },
  });
};

export const useNotificationChannels = () => {
  return useQuery({
    queryKey: ["notification-channels"],
    queryFn: async () => {
      const response = await api.get<NotificationChannel[]>(
        `/notifications`
      );
      return response.data;
    },
  });
};

export const useCreateNotificationChannel = () => {
  return useMutation({
    mutationFn: async (data: CreateNotificationChannelData) => {
      const response = await api.post<NotificationChannel>(
        "/notifications",
        data
      );
      return response.data;
    },
  });
};

export const useUpdateNotificationChannel = () => {
  return useMutation({
    mutationFn: async ({
      channelId,
      data,
    }: {
      channelId: number;
      data: UpdateNotificationChannelData;
    }) => {
      const response = await api.put<NotificationChannel>(
        `/notifications/${channelId}`,
        data
      );
      return response.data;
    },
  });
};

export const useDeleteNotificationChannel = () => {
  return useMutation({
    mutationFn: async (channelId: number) => {
      await api.delete(`/notifications/${channelId}`);
    },
  });
};

interface CategoryInfo {
  id: number;
  name: string;
  slug: string;
}

interface SourceInfo {
  id: number;
  name: string;
  slug: string;
}

interface Article {
  id: number;
  url: string;
  title: string;
  content: string;
  published_date?: string;
  crawled_at: string;
  source_id: number;
  category_id?: number;
  category?: CategoryInfo | null;
  source?: SourceInfo | null;
}

interface ArticlesParams {
  skip?: number;
  limit?: number;
  source_id?: number;
  category_id?: number;
  search?: string;
}

export const useArticles = (params?: ArticlesParams) => {
  return useQuery({
    queryKey: ["articles", params],
    queryFn: async () => {
      const response = await api.get<Article[]>("/articles", { params });
      return response.data;
    },
  });
};

export type { User, Article };
