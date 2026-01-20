"use client";

import { logEvent, setUserId, setUserProperties } from "firebase/analytics";
import { analytics } from "./firebase";

/**
 * Track a custom event in Firebase Analytics
 */
export const trackEvent = (
    eventName: string,
    eventParams?: {
        [key: string]: any;
    }
) => {
    if (!analytics) {
        console.warn("Analytics not initialized, skipping event:", eventName);
        return;
    }

    try {
        logEvent(analytics, eventName, eventParams);
    } catch (error) {
        console.error("Error tracking event:", error);
    }
};

/**
 * Set user ID for analytics
 */
export const setAnalyticsUserId = (userId: string | null) => {
    if (!analytics) return;

    try {
        setUserId(analytics, userId || null);
    } catch (error) {
        console.error("Error setting analytics user ID:", error);
    }
};

/**
 * Set user properties for analytics
 */
export const setAnalyticsUserProperties = (properties: {
    [key: string]: any;
}) => {
    if (!analytics) return;

    try {
        setUserProperties(analytics, properties);
    } catch (error) {
        console.error("Error setting analytics user properties:", error);
    }
};

/**
 * Track page view
 */
export const trackPageView = (pageName: string, pagePath?: string) => {
    trackEvent("page_view", {
        page_name: pageName,
        page_path: pagePath || window.location.pathname,
    });
};

/**
 * Track user login
 */
export const trackLogin = (method: string = "google") => {
    trackEvent("login", {
        method,
    });
};

/**
 * Track user logout
 */
export const trackLogout = () => {
    trackEvent("logout");
};

/**
 * Track category selection
 */
export const trackCategorySelection = (categoryIds: number[], action: "select" | "deselect" | "save") => {
    trackEvent("category_selection", {
        action,
        category_count: categoryIds.length,
        category_ids: categoryIds.join(","),
    });
};

/**
 * Track notification channel setup
 */
export const trackNotificationChannelSetup = (
    provider: string,
    action: "create" | "update" | "delete" | "activate" | "deactivate"
) => {
    trackEvent("notification_channel_setup", {
        provider,
        action,
    });
};

/**
 * Track notification channel test
 */
export const trackNotificationChannelTest = (provider: string, success: boolean) => {
    trackEvent("notification_channel_test", {
        provider,
        success,
    });
};

/**
 * Track error
 */
export const trackError = (errorName: string, errorMessage?: string, errorStack?: string) => {
    trackEvent("error", {
        error_name: errorName,
        error_message: errorMessage,
        error_stack: errorStack?.substring(0, 500), // Limit stack trace length
    });
};
