export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  slug: string;
  description?: string;
}

export interface CategoryUpdate {
  name?: string;
  slug?: string;
  description?: string;
}

export interface UserCategoryPreferenceUpdate {
  category_ids: number[];
}

