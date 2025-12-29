import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import {
  Category,
  CategoryCreate,
  CategoryUpdate,
  UserCategoryPreferenceUpdate,
} from "@/types/category";

// Category CRUD hooks
export const useCategories = () => {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const response = await api.get<Category[]>("/categories");
      return response.data;
    },
  });
};

export const useCategory = (categoryId: number) => {
  return useQuery({
    queryKey: ["category", categoryId],
    queryFn: async () => {
      const response = await api.get<Category>(`/categories/${categoryId}`);
      return response.data;
    },
    enabled: !!categoryId,
  });
};

export const useCategoryBySlug = (slug: string) => {
  return useQuery({
    queryKey: ["category", "slug", slug],
    queryFn: async () => {
      const response = await api.get<Category>(`/categories/slug/${slug}`);
      return response.data;
    },
    enabled: !!slug,
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CategoryCreate) => {
      const response = await api.post<Category>("/categories", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
};

export const useUpdateCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      categoryId,
      data,
    }: {
      categoryId: number;
      data: CategoryUpdate;
    }) => {
      const response = await api.put<Category>(
        `/categories/${categoryId}`,
        data
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
      queryClient.invalidateQueries({ queryKey: ["category", variables.categoryId] });
    },
  });
};

export const useDeleteCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (categoryId: number) => {
      await api.delete(`/categories/${categoryId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categories"] });
    },
  });
};

// User category preferences hooks
export const useUserCategories = () => {
  return useQuery({
    queryKey: ["user-categories"],
    queryFn: async () => {
      const response = await api.get<Category[]>("/categories/me");
      return response.data;
    },
  });
};

export const useUpdateUserCategories = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: UserCategoryPreferenceUpdate) => {
      const response = await api.put<Category[]>(
        "/categories/me",
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-categories"] });
    },
  });
};

