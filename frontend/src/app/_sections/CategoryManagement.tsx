"use client";

import { useState, useEffect } from "react";
import { useCategories, useUserCategories, useUpdateUserCategories } from "@/hooks/useCategories";
import { Tag, CheckCircle2, Circle, Save } from "lucide-react";
import { toast } from "react-toastify";

export default function CategoryManagement() {
  const { data: categories, isLoading } = useCategories();
  const { data: userCategories } = useUserCategories();
  const updatePreferencesMutation = useUpdateUserCategories();

  // Local state to track selected categories
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<Set<number>>(new Set());

  // Sync local state with server state when userCategories loads
  useEffect(() => {
    if (userCategories) {
      setSelectedCategoryIds(new Set(userCategories.map((c) => c.id)));
    }
  }, [userCategories]);

  const handleTogglePreference = (categoryId: number) => {
    setSelectedCategoryIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(categoryId)) {
        newSet.delete(categoryId);
      } else {
        newSet.add(categoryId);
      }
      return newSet;
    });
  };

  const handleSave = async () => {
    const categoryIds = Array.from(selectedCategoryIds);
    try {
      await updatePreferencesMutation.mutateAsync({ category_ids: categoryIds });
      toast.success("Cập nhật thành công!");
    } catch (error: any) {
      const message =
        error.formattedMessage ||
        error.response?.data?.detail ||
        "Đã có lỗi xảy ra.";
      toast.error(message);
    }
  };

  // Check if there are unsaved changes
  const serverCategoryIds = new Set(userCategories?.map((c) => c.id) || []);
  const hasChanges =
    selectedCategoryIds.size !== serverCategoryIds.size ||
    Array.from(selectedCategoryIds).some((id) => !serverCategoryIds.has(id)) ||
    Array.from(serverCategoryIds).some((id) => !selectedCategoryIds.has(id));

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Chọn thể loại bạn muốn theo dõi
        </h3>
        <p className="text-sm text-gray-600">
          Chọn các thể loại bạn muốn theo dõi để nhận thông báo về các bài viết liên quan
        </p>
      </div>

      <div className="space-y-2 mb-6">
        {categories && categories.length > 0 ? (
          categories.map((category) => (
            <label
              key={category.id}
              className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
            >
              <input
                type="checkbox"
                checked={selectedCategoryIds.has(category.id)}
                onChange={() => handleTogglePreference(category.id)}
                disabled={updatePreferencesMutation.isPending}
                className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <Tag className="w-5 h-5 text-gray-600 flex-shrink-0" />
              <div className="flex-1">
                <div className="font-medium text-gray-900">{category.name}</div>
                {category.description && (
                  <div className="text-sm text-gray-500 mt-1">
                    {category.description}
                  </div>
                )}
              </div>
              {selectedCategoryIds.has(category.id) ? (
                <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-gray-300 flex-shrink-0" />
              )}
            </label>
          ))
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Tag className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>Chưa có thể loại nào trong hệ thống.</p>
            <p className="text-sm mt-2">
              Thể loại sẽ được tạo tự động khi hệ thống crawl dữ liệu.
            </p>
          </div>
        )}
      </div>

      {/* Save Button */}
      {categories && categories.length > 0 && (
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            {selectedCategoryIds.size} / {categories.length} thể loại đã chọn
            {hasChanges && (
              <span className="ml-2 text-amber-600 font-medium">
                (Có thay đổi chưa lưu)
              </span>
            )}
          </div>
          <button
            onClick={handleSave}
            disabled={updatePreferencesMutation.isPending || !hasChanges}
            className="flex items-center gap-2 px-3 sm:px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {updatePreferencesMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Đang lưu...</span>
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                <span>Lưu thay đổi</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
