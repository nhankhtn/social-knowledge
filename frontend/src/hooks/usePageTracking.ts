"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { trackPageView } from "@/lib/analytics";

/**
 * Hook to track page views automatically
 */
export const usePageTracking = () => {
    const pathname = usePathname();

    useEffect(() => {
        if (pathname) {
            // Map pathname to readable page name
            const pageName = pathname === "/" ? "Dashboard" : pathname.replace("/", "").charAt(0).toUpperCase() + pathname.slice(2);
            trackPageView(pageName, pathname);
        }
    }, [pathname]);
};
