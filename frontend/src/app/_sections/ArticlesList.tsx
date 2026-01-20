"use client";

import { useState } from "react";
import { useArticles } from "@/hooks/useUser";
import { FileText, ExternalLink, Calendar, Tag } from "lucide-react";

export default function ArticlesList() {
    const [page, setPage] = useState(0);
    const limit = 20;
    const { data: articles, isLoading, refetch } = useArticles({
        skip: page * limit,
        limit,
    });

    const handleLoadArticles = () => {
        refetch();
    };

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
                    Danh sách bài viết
                </h3>
                <p className="text-sm text-gray-600">
                    Xem tất cả các bài viết đã được crawl từ các nguồn tin
                </p>
            </div>

            {!articles && (
                <div className="text-center py-12">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-500 mb-4">Chưa tải danh sách bài viết</p>
                    <button
                        onClick={handleLoadArticles}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        Tải danh sách
                    </button>
                </div>
            )}

            {articles && articles.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p>Chưa có bài viết nào trong hệ thống.</p>
                </div>
            )}

            {articles && articles.length > 0 && (
                <>
                    <div className="space-y-4 mb-6">
                        {articles.map((article) => (
                            <div
                                key={article.id}
                                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                        <h4 className="font-medium text-gray-900 mb-2">
                                            {article.title}
                                        </h4>
                                        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                                            {article.content.substring(0, 200)}...
                                        </p>
                                        <div className="flex items-center gap-4 text-xs text-gray-500">
                                            {article.published_date && (
                                                <div className="flex items-center gap-1">
                                                    <Calendar className="w-4 h-4" />
                                                    <span>
                                                        {new Date(article.published_date).toLocaleDateString(
                                                            "vi-VN"
                                                        )}
                                                    </span>
                                                </div>
                                            )}
                                            {article.category_id && (
                                                <div className="flex items-center gap-1">
                                                    <Tag className="w-4 h-4" />
                                                    <span>Category ID: {article.category_id}</span>
                                                </div>
                                            )}
                                            <span>Source ID: {article.source_id}</span>
                                        </div>
                                    </div>
                                    <a
                                        href={article.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
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
                        <span className="text-sm text-gray-600">
                            Trang {page + 1}
                        </span>
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
    );
}
