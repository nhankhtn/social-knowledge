"use client";

import { useState } from "react";
import { useSummaries } from "@/hooks/useUser";
import { useCategories } from "@/hooks/useCategories";
import { Calendar, Tag, Search, X, Filter, Bell } from "lucide-react";

export default function SentSummariesList() {
  const [page, setPage] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [tempSearchQuery, setTempSearchQuery] = useState("");

  const limit = 20;

  const { data: categories } = useCategories();

  const { data: summaries, isLoading } = useSummaries({
    skip: page * limit,
    limit,
    category_id: selectedCategory || undefined,
    search: searchQuery || undefined,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    setSearchQuery(tempSearchQuery);
  };

  const handleResetFilters = () => {
    setSelectedCategory(null);
    setTempSearchQuery("");
    setSearchQuery("");
    setPage(0);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-6 flex flex-col gap-2">
        <h3 className="text-lg font-semibold text-gray-900">
          Tất cả bài đã được tóm tắt
        </h3>
        <p className="text-sm text-gray-600">
          Xem tất cả các bài báo trong hệ thống đã được AI tóm tắt, có thể lọc theo thể loại và tìm kiếm.
        </p>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={tempSearchQuery}
              onChange={(e) => setTempSearchQuery(e.target.value)}
              placeholder="Tìm kiếm theo tiêu đề hoặc nội dung tóm tắt..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Tìm kiếm
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Bộ lọc:</span>
          </div>

          <select
            value={selectedCategory ?? ""}
            onChange={(e) =>
              setSelectedCategory(
                e.target.value ? parseInt(e.target.value, 10) : null
              )
            }
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          >
            <option value="">Tất cả thể loại</option>
            {categories?.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          {(selectedCategory || searchQuery) && (
            <button
              type="button"
              onClick={handleResetFilters}
              className="flex items-center gap-1 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <X className="w-4 h-4" />
              Xóa bộ lọc
            </button>
          )}
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      )}

      {/* Empty state */}
      {!isLoading && summaries && summaries.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Bell className="w-10 h-10 mx-auto mb-3 text-gray-400" />
          <p>
            Chưa có bài viết nào được tóm tắt.
          </p>
        </div>
      )}

      {/* List */}
      {summaries && summaries.length > 0 && (
        <>
          <div className="space-y-4 mb-6">
            {summaries.map((item) => (
              <div
                key={item.article_id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex flex-col gap-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h4 className="font-medium text-gray-900">
                      {item.title}
                    </h4>
                    <div className="flex items-center gap-3 text-xs text-gray-500 flex-wrap">
                      {item.category && (
                        <span className="flex items-center gap-1">
                          <Tag className="w-4 h-4" />
                          <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded">
                            {item.category.name}
                          </span>
                        </span>
                      )}
                      {item.source && (
                        <span className="text-gray-500">
                          Nguồn: {item.source.name}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(item.summarized_at).toLocaleString("vi-VN", {
                            year: "numeric",
                            month: "2-digit",
                            day: "2-digit",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {item.summary_text}
                  </p>

                    {item.url && (
                    <div className="pt-1">
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        Mở bài gốc
                      </a>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 text-sm"
            >
              Trước
            </button>
            <span className="text-sm text-gray-600">Trang {page + 1}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={summaries.length < limit}
              className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 text-sm"
            >
              Sau
            </button>
          </div>
        </>
      )}
    </div>
  );
}

