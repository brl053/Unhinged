import { useMutation } from '@tanstack/react-query';

const API_BASE_URL = "http://localhost:8080";

// Define response type for clarity
interface ResponseData {
  response: string;
}

export const useSendMessage = () => {
  return useMutation<ResponseData, Error, string>({
    mutationFn: async (message: string) => {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: message }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      return response.json(); // This will return ResponseData
    }
  });
};
