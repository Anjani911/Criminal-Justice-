import api from '@/api/client';

export const chatService = {
  async sendMessage(question: string, context?: Record<string, unknown>, language = 'English') {
    const { data } = await api.post('/chat', {
      question,
      context: {
        ...(context ?? {}),
        language,
      },
    });
    return data;
  },
};
