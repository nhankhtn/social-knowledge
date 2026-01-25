"use client";

import { Formik, Form, Field } from "formik";
import { useNotificationStore } from "@/store/notificationStore";
import { Save, MessageSquare, Send, HelpCircle, ChevronRight, ExternalLink, ChevronDown } from "lucide-react";
import { useState, useEffect } from "react";
import {
  useCreateNotificationChannel,
  useUpdateNotificationChannel,
  useNotificationChannels,
} from "@/hooks/useUser";
import { toast } from "react-toastify";
import { trackNotificationChannelSetup } from "@/lib/analytics";

type NotificationFormData = {
  provider: "discord_webhook" | "telegram_bot" | "slack_webhook";
  url?: string;
  token?: string;
  chatId?: string;
  is_active: boolean;
  notification_hours: number[];
};

export default function NotificationForm() {
  const { provider, credentials, setProvider, setCredentials } =
    useNotificationStore();

  // Get all channels (including inactive) to check for duplicates
  const { data: channels, refetch } = useNotificationChannels();
  const createChannelMutation = useCreateNotificationChannel();
  const updateChannelMutation = useUpdateNotificationChannel();
  const [selectedProvider, setSelectedProvider] = useState<string>(provider);
  const [showInstructions, setShowInstructions] = useState<Record<string, boolean>>({
    discord_webhook: false,
    telegram_bot: false,
    slack_webhook: false,
  });

  // Load existing channel when channels data changes
  useEffect(() => {
    if (channels && channels.length > 0) {
      // First try to find channel matching selected provider (active or inactive)
      let channelToLoad = channels.find(
        (c) => c.provider === selectedProvider
      );

      // If not found, try any active channel
      if (!channelToLoad) {
        channelToLoad = channels.find((c) => c.is_active);
      }

      // If still not found, use first channel (even if inactive)
      if (!channelToLoad) {
        channelToLoad = channels[0];
      }

      if (channelToLoad) {
        // Only update if different from current state
        if (channelToLoad.provider !== selectedProvider) {
          setProvider(channelToLoad.provider as any);
          setSelectedProvider(channelToLoad.provider);
        }
        setCredentials(channelToLoad.credentials);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [channels]);

  // Load channel when provider selection changes (via radio button)
  useEffect(() => {
    if (channels && channels.length > 0 && selectedProvider) {
      const channelForProvider = channels.find(
        (c) => c.provider === selectedProvider
      );

      if (channelForProvider) {
        setProvider(channelForProvider.provider as any);
        setCredentials(channelForProvider.credentials);
        // Update form field values when switching providers
        // This will trigger Formik's enableReinitialize to update the form
      } else {
        // No channel for this provider yet, clear credentials
        setCredentials({});
      }
    }
  }, [selectedProvider, channels, setProvider, setCredentials]);

  // Get current channel based on selected provider
  const currentChannel = channels?.find((c) => c.provider === (selectedProvider || provider));

  // Calculate initial values based on current channel or store state
  const getInitialValues = (): NotificationFormData => {
    if (currentChannel) {
      return {
        provider: currentChannel.provider as any,
        url: currentChannel.credentials?.url || "",
        token: currentChannel.credentials?.token || "",
        chatId: currentChannel.credentials?.chat_id || "",
        is_active: currentChannel.is_active ?? false,
        notification_hours: currentChannel.notification_hours || [],
      };
    }
    return {
      provider: (selectedProvider || provider || "discord_webhook") as any,
      url: credentials?.url || "",
      token: credentials?.token || "",
      chatId: credentials?.chat_id || "",
      is_active: false,
      notification_hours: [],
    };
  };

  const initialValues = getInitialValues();

  const onSubmit = async (
    values: NotificationFormData,
    { setSubmitting }: any
  ) => {
    const creds: Record<string, any> = {};
    if (values.provider === "telegram_bot") {
      creds.token = values.token;
      creds.chat_id = values.chatId;
    } else {
      creds.url = values.url;
    }

    setProvider(values.provider);
    setCredentials(creds);

    try {
      const existingChannel = channels?.find(
        (c) => c.provider === values.provider
      );

      if (existingChannel) {
        await updateChannelMutation.mutateAsync({
          channelId: existingChannel.id,
          data: {
            provider: values.provider,
            credentials: creds,
            is_active: values.is_active ?? true,
            notification_hours: values.notification_hours,
          },
        });
        trackNotificationChannelSetup(
          values.provider,
          values.is_active ? "activate" : "deactivate"
        );
        trackNotificationChannelSetup(values.provider, "update");
      } else {
        await createChannelMutation.mutateAsync({
          provider: values.provider,
          credentials: creds,
          name: `${values.provider} notification`,
          notification_hours: values.notification_hours,
        });
        trackNotificationChannelSetup(values.provider, "create");
      }

      await refetch();
      toast.success("Cấu hình thông báo đã được lưu thành công!");
    } catch (error: any) {
      console.error(
        "Error saving notification channel:",
        error.response?.data || error.message
      );
      toast.error("Đã có lỗi xảy ra khi lưu cấu hình.");
    } finally {
      setSubmitting(false);
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
        return <MessageSquare className='w-5 h-5' />;
    }
  };

  const toggleInstructions = (provider: string) => {
    setShowInstructions(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  const InstructionPanel = ({ provider, children }: { provider: string; children: React.ReactNode }) => {
    const isOpen = showInstructions[provider] || false;
    const providerName = provider === 'discord_webhook' ? 'Discord' : provider === 'telegram_bot' ? 'Telegram' : 'Slack';
    return (
      <div className='border border-gray-200 rounded-lg overflow-hidden'>
        <button
          type='button'
          onClick={() => toggleInstructions(provider)}
          className='w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors'
        >
          <div className='flex items-center gap-2'>
            <HelpCircle className='w-5 h-5 text-indigo-600' />
            <span className='text-sm font-medium text-gray-700'>
              Hướng dẫn cài đặt {providerName}
            </span>
          </div>
          {isOpen ? (
            <ChevronDown className='w-5 h-5 text-gray-500' />
          ) : (
            <ChevronRight className='w-5 h-5 text-gray-500' />
          )}
        </button>
        {isOpen && (
          <div className='p-4 bg-white border-t border-gray-200'>
            {children}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className='bg-white rounded-xl shadow-sm border border-gray-200 p-6'>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        enableReinitialize
      >
        {({ values, isSubmitting, setFieldValue }: any) => {
          const currentProvider = values.provider || selectedProvider;

          const handleHourToggle = (hour: number) => {
            const currentHours = values.notification_hours || [];
            const newHours = currentHours.includes(hour)
              ? currentHours.filter((h: number) => h !== hour)
              : [...currentHours, hour].sort((a: number, b: number) => a - b);
            setFieldValue('notification_hours', newHours);
          };

          return (
            <Form className='space-y-6'>
              {/* Provider Selection */}
              <div>
                <label className='block text-sm font-medium text-gray-700 mb-3'>
                  Loại kênh thông báo
                </label>
                <div className='grid grid-cols-3 gap-3'>
                  <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
                    <Field
                      type='radio'
                      name='provider'
                      value='discord_webhook'
                      className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
                      onChange={(e: any) => {
                        setFieldValue("provider", e.target.value);
                        setSelectedProvider(e.target.value);
                      }}
                    />
                    <MessageSquare className='w-5 h-5 text-gray-600' />
                    <span className='text-sm font-medium text-gray-700'>
                      Discord
                    </span>
                  </label>
                  <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
                    <Field
                      type='radio'
                      name='provider'
                      value='telegram_bot'
                      className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
                      onChange={(e: any) => {
                        setFieldValue("provider", e.target.value);
                        setSelectedProvider(e.target.value);
                      }}
                    />
                    <Send className='w-5 h-5 text-gray-600' />
                    <span className='text-sm font-medium text-gray-700'>
                      Telegram
                    </span>
                  </label>
                  <label className='flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors'>
                    <Field
                      type='radio'
                      name='provider'
                      value='slack_webhook'
                      className='w-4 h-4 text-indigo-600 focus:ring-indigo-500'
                      onChange={(e: any) => {
                        setFieldValue("provider", e.target.value);
                        setSelectedProvider(e.target.value);
                      }}
                    />
                    <MessageSquare className='w-5 h-5 text-gray-600' />
                    <span className='text-sm font-medium text-gray-700'>
                      Slack
                    </span>
                  </label>
                </div>
              </div>

              {/* Instructions */}
              {currentProvider === "discord_webhook" && (
                <InstructionPanel provider="discord_webhook">
                  <div className='space-y-4 text-sm text-gray-700'>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 1: Tạo Webhook trong Discord</h4>
                      <ol className='list-decimal list-inside space-y-1 ml-2'>
                        <li>Mở Discord và vào server của bạn</li>
                        <li>Chọn channel bạn muốn nhận thông báo</li>
                        <li>Click vào biểu tượng <strong>⚙️ Settings</strong> (hoặc chuột phải vào channel)</li>
                        <li>Chọn <strong>Integrations</strong> → <strong>Webhooks</strong></li>
                        <li>Click <strong>New Webhook</strong></li>
                        <li>Đặt tên cho webhook (ví dụ: "Social Knowledge Bot")</li>
                        <li>Click <strong>Copy Webhook URL</strong></li>
                      </ol>
                    </div>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 2: Dán Webhook URL</h4>
                      <p>Dán URL bạn vừa copy vào ô <strong>Webhook URL</strong> bên dưới</p>
                    </div>
                    <div className='bg-blue-50 border border-blue-200 rounded p-3'>
                      <p className='text-xs text-blue-800'>
                        <strong>Lưu ý:</strong> Webhook URL có dạng: <code className='bg-blue-100 px-1 rounded'>https://discord.com/api/webhooks/...</code>
                      </p>
                    </div>
                  </div>
                </InstructionPanel>
              )}

              {currentProvider === "telegram_bot" && (
                <InstructionPanel provider="telegram_bot">
                  <div className='space-y-4 text-sm text-gray-700'>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 1: Tạo Bot Token</h4>
                      <ol className='list-decimal list-inside space-y-1 ml-2'>
                        <li>Mở Telegram và tìm <strong>@BotFather</strong></li>
                        <li>Gửi lệnh <code className='bg-gray-100 px-1 rounded'>/newbot</code></li>
                        <li>Làm theo hướng dẫn để đặt tên cho bot</li>
                        <li>BotFather sẽ cung cấp cho bạn một <strong>Bot Token</strong></li>
                        <li>Copy token này (có dạng: <code className='bg-gray-100 px-1 rounded'>123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11</code>)</li>
                      </ol>
                    </div>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 2: Lấy Chat ID</h4>
                      <ol className='list-decimal list-inside space-y-1 ml-2'>
                        <li>Gửi một tin nhắn bất kỳ đến bot của bạn hoặc vào group/channel</li>
                        <li>Truy cập: <a href='https://api.telegram.org/bot&lt;YOUR_BOT_TOKEN&gt;/getUpdates' target='_blank' rel='noopener noreferrer' className='text-indigo-600 hover:underline inline-flex items-center gap-1'>https://api.telegram.org/bot&lt;YOUR_BOT_TOKEN&gt;/getUpdates <ExternalLink className='w-3 h-3' /></a></li>
                        <li>Thay <code className='bg-gray-100 px-1 rounded'>&lt;YOUR_BOT_TOKEN&gt;</code> bằng token của bạn</li>
                        <li>Tìm <code className='bg-gray-100 px-1 rounded'>chat id</code> trong kết quả trả về (tìm phần có dạng: <code className='bg-gray-100 px-1 rounded'>chat id</code>)</li>
                        <li>Copy số ID (có thể là số dương hoặc số âm, ví dụ: <code className='bg-gray-100 px-1 rounded'>-1001234567890</code>)</li>
                      </ol>
                    </div>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 3: Điền thông tin</h4>
                      <p>Dán Bot Token và Chat ID vào các ô tương ứng bên dưới</p>
                    </div>
                    <div className='bg-blue-50 border border-blue-200 rounded p-3'>
                      <p className='text-xs text-blue-800'>
                        <strong>Mẹo:</strong> Để lấy Chat ID dễ hơn, bạn có thể dùng bot <strong>@userinfobot</strong> hoặc <strong>@getidsbot</strong>
                      </p>
                    </div>
                  </div>
                </InstructionPanel>
              )}

              {currentProvider === "slack_webhook" && (
                <InstructionPanel provider="slack_webhook">
                  <div className='space-y-4 text-sm text-gray-700'>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 1: Tạo Slack App</h4>
                      <ol className='list-decimal list-inside space-y-1 ml-2'>
                        <li>Truy cập <a href='https://api.slack.com/apps' target='_blank' rel='noopener noreferrer' className='text-indigo-600 hover:underline inline-flex items-center gap-1'>Slack API <ExternalLink className='w-3 h-3' /></a></li>
                        <li>Click <strong>Create New App</strong> → <strong>From scratch</strong></li>
                        <li>Đặt tên app (ví dụ: "Social Knowledge") và chọn workspace</li>
                        <li>Click <strong>Create App</strong></li>
                      </ol>
                    </div>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 2: Kích hoạt Incoming Webhooks</h4>
                      <ol className='list-decimal list-inside space-y-1 ml-2'>
                        <li>Trong trang app settings, chọn <strong>Incoming Webhooks</strong> ở menu bên trái</li>
                        <li>Bật toggle <strong>Activate Incoming Webhooks</strong></li>
                        <li>Click <strong>Add New Webhook to Workspace</strong></li>
                        <li>Chọn channel bạn muốn nhận thông báo</li>
                        <li>Click <strong>Allow</strong></li>
                      </ol>
                    </div>
                    <div>
                      <h4 className='font-semibold mb-2'>Bước 3: Copy Webhook URL</h4>
                      <ol className='list-decimal list-inside space-y-1 ml-2'>
                        <li>Sau khi tạo webhook, bạn sẽ thấy <strong>Webhook URL</strong></li>
                        <li>Click <strong>Copy</strong> để sao chép URL</li>
                        <li>Dán URL vào ô <strong>Webhook URL</strong> bên dưới</li>
                      </ol>
                    </div>
                    <div className='bg-blue-50 border border-blue-200 rounded p-3'>
                      <p className='text-xs text-blue-800'>
                        <strong>Lưu ý:</strong> Webhook URL có dạng: <code className='bg-blue-100 px-1 rounded'>https://hooks.slack.com/services/T.../B.../...</code>
                      </p>
                    </div>
                  </div>
                </InstructionPanel>
              )}

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
                    <Field
                      id='token'
                      name='token'
                      type='text'
                      placeholder='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
                      className='block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors'
                    />
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
                    <Field
                      id='chatId'
                      name='chatId'
                      type='text'
                      placeholder='-1001234567890'
                      className='block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors'
                    />
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
                    <Field
                      id='url'
                      name='url'
                      type='text'
                      placeholder={
                        currentProvider === "discord_webhook"
                          ? "https://discord.com/api/webhooks/..."
                          : currentProvider === "slack_webhook"
                            ? "https://hooks.slack.com/services/..."
                            : "https://your-webhook-url.com/..."
                      }
                      className='block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-colors'
                    />
                  </div>
                  <p className='mt-2 text-sm text-gray-500'>
                    {currentProvider === "discord_webhook"
                      ? "Webhook URL từ Discord channel settings"
                      : "Webhook URL từ Slack App settings"}
                  </p>
                </div>
              )}

              {/* Notification Hours Selection */}
              <div className='p-4 bg-gray-50 rounded-lg'>
                <div className='mb-3'>
                  <label className='block text-sm font-medium text-gray-700 mb-1'>
                    Giờ nhận thông báo
                  </label>
                  <p className='text-sm text-gray-500'>
                    Chọn các giờ trong ngày (0-23h) để nhận thông báo. Để trống để nhận mọi lúc.
                  </p>
                </div>
                <div className='grid grid-cols-6 sm:grid-cols-8 md:grid-cols-12 gap-2'>
                  {Array.from({ length: 24 }, (_, i) => i).map((hour) => {
                    const isSelected = (values.notification_hours || []).includes(hour);
                    return (
                      <button
                        key={hour}
                        type='button'
                        onClick={() => handleHourToggle(hour)}
                        className={`relative flex items-center justify-center p-2 border rounded-lg cursor-pointer transition-colors ${isSelected
                          ? 'bg-indigo-50 border-indigo-600 text-indigo-600 font-semibold'
                          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-100'
                          }`}
                      >
                        <span className='text-sm'>{hour}h</span>
                      </button>
                    );
                  })}
                </div>
                {values.notification_hours && values.notification_hours.length > 0 && (
                  <p className='mt-3 text-sm text-gray-600'>
                    Đã chọn: {values.notification_hours.sort((a: number, b: number) => a - b).join('h, ')}h
                  </p>
                )}
              </div>

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
                  <Field
                    id='is_active'
                    name='is_active'
                    type='checkbox'
                    className='sr-only peer'
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
            </Form>
          );
        }}
      </Formik>
    </div>
  );
}
