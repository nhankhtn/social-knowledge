"use client";

import { useState } from "react";
import { useArticles } from "@/hooks/useUser";
import { useCategories } from "@/hooks/useCategories";
import { FileText, ExternalLink, Calendar, Tag, Search, X } from "lucide-react";

interface ArticleDialogProps {
    article: {
        id: number;
        title: string;
        content: string;
        url: string;
        published_date?: string;
        category?: { id: number; name: string; slug: string } | null;
        source?: { id: number; name: string; slug: string } | null;
    } | null;
    isOpen: boolean;
    onClose: () => void;
}

function ArticleDialog({ article, isOpen, onClose }: ArticleDialogProps) {
    if (!isOpen || !article) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
            <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-900">{article.title}</h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    <div className="mb-4 flex items-center gap-4 text-sm text-gray-600">
                        {article.published_date && (
                            <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                <span>
                                    {new Date(article.published_date).toLocaleDateString("vi-VN", {
                                        year: "numeric",
                                        month: "long",
                                        day: "numeric",
                                        hour: "2-digit",
                                        minute: "2-digit",
                                    })}
                                </span>
                            </div>
                        )}
                        {article.category && (
                            <div className="flex items-center gap-1">
                                <Tag className="w-4 h-4" />
                                <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded">
                                    {article.category.name}
                                </span>
                            </div>
                        )}
                        {article.source && (
                            <span className="text-gray-500">Nguồn: {article.source.name}</span>
                        )}
                    </div>

                    <div className="prose max-w-none">
                        <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                            {article.content}
                        </div>
                    </div>
                </div>

                <div className="p-6 border-t border-gray-200 flex items-center justify-between">
                    <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                        <ExternalLink className="w-4 h-4" />
                        Đọc bài gốc
                    </a>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                        Đóng
                    </button>
                </div>
            </div>
        </div>
    );
}

export default function ArticlesList() {
    const [page, setPage] = useState(0);
    const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [tempSearchQuery, setTempSearchQuery] = useState("");
    const [selectedArticle, setSelectedArticle] = useState<ArticleDialogProps["article"]>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const limit = 20;
    const { data: articles, isLoading } = useArticles({
        skip: page * limit,
        limit,
        category_id: selectedCategory || undefined,
        search: searchQuery || undefined,
    });

    const { data: categories } = useCategories();

    const handleArticleClick = (article: any) => {
        setSelectedArticle(article);
        setIsDialogOpen(true);
    };

    const handleCloseDialog = () => {
        setIsDialogOpen(false);
        setSelectedArticle(null);
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(0); // Reset to first page when searching
        setSearchQuery(tempSearchQuery);
    };

    const handleCategoryChange = (categoryId: number | null) => {
        setSelectedCategory(categoryId);
        setPage(0); // Reset to first page when filtering
    };

    return (
        <>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Danh sách bài viết
                    </h3>
                    <p className="text-sm text-gray-600">
                        Xem tất cả các bài viết đã được crawl từ các nguồn tin
                    </p>
                </div>

                {/* Filters and Search */}
                <div className="mb-6 space-y-4">
                    <form onSubmit={handleSearch} className="flex gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={tempSearchQuery}
                                onChange={(e) => setTempSearchQuery(e.target.value)}
                                placeholder="Tìm kiếm theo tiêu đề hoặc nội dung..."
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

                    <div className="flex items-center gap-4">
                        <label className="text-sm font-medium text-gray-700">Lọc theo thể loại:</label>
                        <select
                            value={selectedCategory || ""}
                            onChange={(e) => handleCategoryChange(e.target.value ? parseInt(e.target.value) : null)}
                            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            <option value="">Tất cả</option>
                            {categories?.map((category) => (
                                <option key={category.id} value={category.id}>
                                    {category.name}
                                </option>
                            ))}
                        </select>
                        {(selectedCategory || searchQuery) && (
                            <button
                                onClick={() => {
                                    setSelectedCategory(null);
                                    setTempSearchQuery("");
                                    setPage(0);
                                }}
                                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                                Xóa bộ lọc
                            </button>
                        )}
                    </div>
                </div>

                {isLoading && <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    </div>
                </div>}

                {articles && articles.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>
                            {searchQuery || selectedCategory
                                ? "Không tìm thấy bài viết nào phù hợp."
                                : "Chưa có bài viết nào trong hệ thống."}
                        </p>
                    </div>
                )}

                {articles && articles.length > 0 && (
                    <>
                        <div className="space-y-4 mb-6">
                            {articles.map((article) => (
                                <div
                                    key={article.id}
                                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                                    onClick={() => handleArticleClick(article)}
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex-1">
                                            <h4 className="font-medium text-gray-900 mb-2">
                                                {article.title}
                                            </h4>
                                            <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                                                {article.content.substring(0, 200)}...
                                            </p>
                                            <div className="flex items-center gap-4 text-xs text-gray-500 flex-wrap">
                                                {article.published_date && (
                                                    <div className="flex items-center gap-1">
                                                        <Calendar className="w-4 h-4" />
                                                        <span>
                                                            {new Date(article.published_date).toLocaleDateString("vi-VN")}
                                                        </span>
                                                    </div>
                                                )}
                                                {article.category && (
                                                    <div className="flex items-center gap-1">
                                                        <Tag className="w-4 h-4" />
                                                        <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded">
                                                            {article.category.name}
                                                        </span>
                                                    </div>
                                                )}
                                                {article.source && (
                                                    <span>Nguồn: {article.source.name}</span>
                                                )}
                                            </div>
                                        </div>
                                        <a
                                            href={article.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            onClick={(e) => e.stopPropagation()}
                                            className="flex items-center gap-1 text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                                        >
                                            <ExternalLink className="w-4 h-4" />
                                            Xem
                                        </a>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                            <button
                                onClick={() => setPage((p) => Math.max(0, p - 1))}
                                disabled={page === 0}
                                className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                            >
                                Trước
                            </button>
                            <span className="text-sm text-gray-600">Trang {page + 1}</span>
                            <button
                                onClick={() => setPage((p) => p + 1)}
                                disabled={articles.length < limit}
                                className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                            >
                                Sau
                            </button>
                        </div>
                    </>
                )}
            </div>

            <ArticleDialog
                article={selectedArticle}
                isOpen={isDialogOpen}
                onClose={handleCloseDialog}
            />
        </>
    );
}
