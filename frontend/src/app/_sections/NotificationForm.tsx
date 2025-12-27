"use client";

import { useForm } from "react-hook-form";
import { useNotificationStore } from "@/store/notificationStore";
import { Save, Bell, MessageSquare, Send } from "lucide-react";
import { useState, useEffect } from "react";
import {
  useCreateNotificationChannel,
  useUpdateNotificationChannel,
  useNotificationChannels,
} from "@/hooks/useUser";
import { toast } from "react-toastify";

type NotificationFormData = {
  provider: "discord_webhook" | "telegram_bot" | "slack_webhook" | "custom";
  url?: string;
  token?: string;
  chatId?: string;
  is_active?: boolean;
};

export default function NotificationForm() {
  const { provider, credentials, setProvider, setCredentials } =
    useNotificationStore();

  const { data: channels, refetch } = useNotificationChannels();
  const createChannelMutation = useCreateNotificationChannel();
  const updateChannelMutation = useUpdateNotificationChannel();
  const [selectedProvider, setSelectedProvider] = useState<string>(provider);

  // Load existing channel
  useEffect(() => {
    if (channels && channels.length > 0) {
      const firstChannel = channels[0];
      setProvider(firstChannel.provider as any);
      setCredentials(firstChannel.credentials);
      setSelectedProvider(firstChannel.provider);
    }
  }, [channels]);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    reset,
  } = useForm<NotificationFormData>({
    defaultValues: {
      provider: provider,
      url: credentials?.url || "",
      token: credentials?.token || "",
      chatId: credentials?.chat_id || "",
      is_active: true,
    },
  });

  const currentProvider = watch("provider") || selectedProvider;

  // Reset form when provider changes
  useEffect(() => {
    setSelectedProvider(currentProvider);
  }, [currentProvider]);

  const onSubmit = async (data: NotificationFormData) => {
    const creds: Record<string, any> = {};
    if (data.provider === "telegram_bot") {
      creds.token = data.token;
      creds.chat_id = data.chatId;
    } else {
      creds.url = data.url;
    }

    setProvider(data.provider);
    setCredentials(creds);

    try {
      const existingChannel = channels?.find(
        (c) => c.provider === data.provider
      );

      if (existingChannel) {
        await updateChannelMutation.mutateAsync({
          channelId: existingChannel.id,
          data: {
            provider: data.provider,
            credentials: creds,
            is_active: data.is_active ?? true,
          },
        });
      } else {
        await createChannelMutation.mutateAsync({
          provider: data.provider,
          credentials: creds,
          name: `${data.provider} notification`,
        });
      }

      await refetch();
      toast.success("Cấu hình thông báo đã được lưu thành công!");
    } catch (error: any) {
      console.error(
        "Error saving notification channel:",
        error.response?.data || error.message
      );
      toast.error("Đã có lỗi xảy ra khi lưu cấu hình.", error);
    }
  };

  const getProviderIcon = (prov: string) => {
    switch (prov) {
      case "discord_webhook":
        return <MessageSquare className='w-5 h-5' />;
      case "telegram_bot":
        return <Send className='w-5 h-5' />;
      case "slack_webhook":
        return <MessageSquare className='w-5 h-5' />;
      default:
        return <Bell className='w-5 h-5' />;
    }
  };

  return (
    <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
      <form onSubmit={handleSubmit(onSubmit)} className='space-y-6'>
        {/* Provider Selection */}
        <div>
          <label className='block text-sm font-medium text-gray-700 mb-3'>
            Loại kênh thông báo
          </label>
          <div className='grid grid-cols-2 gap-3'>
            <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
              <input
                type='radio'
                value='discord_webhook'
                {...register("provider")}
                className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
              />
              <MessageSquare className='w-5 h-5 text-gray-600' />
              <span className='text-sm font-medium text-gray-700'>Discord</span>
            </label>
            <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
              <input
                type='radio'
                value='telegram_bot'
                {...register("provider")}
                className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
              />
              <Send className='w-5 h-5 text-gray-600' />
              <span className='text-sm font-medium text-gray-700'>
                Telegram
              </span>
            </label>
            <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
              <input
                type='radio'
                value='slack_webhook'
                {...register("provider")}
                className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
              />
              <MessageSquare className='w-5 h-5 text-gray-600' />
              <span className='text-sm font-medium text-gray-700'>Slack</span>
            </label>
            <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
              <input
                type='radio'
                value='custom'
                {...register("provider")}
                className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
              />
              <Bell className='w-5 h-5 text-gray-600' />
              <span className='text-sm font-medium text-gray-700'>Custom</span>
            </label>
          </div>
        </div>

        {/* Conditional Fields */}
        {currentProvider === "telegram_bot" ? (
          <>
            {/* Telegram Bot Token */}
            <div>
              <label
                htmlFor='token'
                className='block text-sm font-medium text-gray-700 mb-2'
              >
                Bot Token
              </label>
              <input
                id='token'
                type='text'
                placeholder='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
                {...register("token")}
                className='block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors'
              />
              {errors.token && (
                <p className='mt-2 text-sm text-red-600'>
                  {errors.token.message}
                </p>
              )}
              <p className='mt-2 text-sm text-gray-500'>
                Lấy từ @BotFather trên Telegram
              </p>
            </div>

            {/* Telegram Chat ID */}
            <div>
              <label
                htmlFor='chatId'
                className='block text-sm font-medium text-gray-700 mb-2'
              >
                Chat ID
              </label>
              <input
                id='chatId'
                type='text'
                placeholder='-1001234567890'
                {...register("chatId")}
                className='block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors'
              />
              {errors.chatId && (
                <p className='mt-2 text-sm text-red-600'>
                  {errors.chatId.message}
                </p>
              )}
              <p className='mt-2 text-sm text-gray-500'>
                ID của chat/channel/group cần gửi tin
              </p>
            </div>
          </>
        ) : (
          /* Webhook URL */
          <div>
            <label
              htmlFor='url'
              className='block text-sm font-medium text-gray-700 mb-2'
            >
              Webhook URL
            </label>
            <div className='relative'>
              <div className='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none'>
                {getProviderIcon(currentProvider)}
              </div>
              <input
                id='url'
                type='text'
                placeholder={
                  currentProvider === "discord_webhook"
                    ? "https://discord.com/api/webhooks/..."
                    : currentProvider === "slack_webhook"
                    ? "https://hooks.slack.com/services/..."
                    : "https://your-webhook-url.com/..."
                }
                {...register("url")}
                className='block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors'
              />
            </div>
            {errors.url && (
              <p className='mt-2 text-sm text-red-600'>{errors.url.message}</p>
            )}
            <p className='mt-2 text-sm text-gray-500'>
              {currentProvider === "discord_webhook"
                ? "Webhook URL từ Discord channel settings"
                : currentProvider === "slack_webhook"
                ? "Webhook URL từ Slack App settings"
                : "Custom webhook URL của bạn"}
            </p>
          </div>
        )}

        {/* Active Toggle */}
        <div className='flex items-center justify-between p-4 bg-gray-50 rounded-lg'>
          <div>
            <label
              htmlFor='is_active'
              className='block text-sm font-medium text-gray-700'
            >
              Kích hoạt thông báo
            </label>
            <p className='text-sm text-gray-500 mt-1'>
              Bật để nhận thông báo tự động từ hệ thống
            </p>
          </div>
          <label className='relative inline-flex items-center cursor-pointer'>
            <input
              id='is_active'
              type='checkbox'
              {...register("is_active")}
              className='sr-only peer'
              defaultChecked
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
          </label>
        </div>

        {/* Submit Button */}
        <div className='flex items-center justify-between pt-4 border-t border-gray-200'>
          <button
            type='submit'
            disabled={isSubmitting}
            className='flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
          >
            {isSubmitting ? (
              <>
                <div className='animate-spin rounded-full h-5 w-5 border-b-2 border-white'></div>
                <span>Đang lưu...</span>
              </>
            ) : (
              <>
                <Save className='w-5 h-5' />
                <span>Lưu cấu hình</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
