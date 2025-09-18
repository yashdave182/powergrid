// Direct Gemini API Service
interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

interface GeminiError {
  error: {
    message: string;
    code: number;
  };
}

class GeminiApiService {
  private apiKey: string;
  private baseUrl: string = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async generateContent(prompt: string): Promise<string> {
    if (!this.apiKey || this.apiKey === 'your-api-key-here') {
      throw new Error('Please set your Gemini API key in the environment variables');
    }

    try {
      const response = await fetch(`${this.baseUrl}?key=${this.apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: prompt
            }]
          }]
        })
      });

      if (!response.ok) {
        const errorData: GeminiError = await response.json();
        throw new Error(`Gemini API Error: ${errorData.error?.message || 'Unknown error'}`);
      }

      const data: GeminiResponse = await response.json();
      
      if (!data.candidates || data.candidates.length === 0) {
        throw new Error('No response generated from Gemini API');
      }

      return data.candidates[0].content.parts[0].text;
    } catch (error) {
      console.error('Gemini API Error:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to connect to Gemini API');
    }
  }

  async analyzeMarineData(data: any): Promise<string> {
    const prompt = `As a marine biology expert, analyze the following data and provide insights about marine biodiversity, ecosystem health, and conservation recommendations:

Data: ${JSON.stringify(data, null, 2)}

Please provide:
1. Analysis of the data
2. Key insights about biodiversity patterns
3. Conservation recommendations
4. Potential threats or opportunities

Format your response in a clear, structured manner.`;

    return this.generateContent(prompt);
  }

  async chatAboutMarine(question: string, contextData?: any): Promise<string> {
    let prompt = `As a marine biology and oceanography expert, please answer the following question: ${question}`;
    
    if (contextData) {
      prompt += `\n\nContext data for reference: ${JSON.stringify(contextData, null, 2)}`;
    }

    prompt += `\n\nPlease provide a comprehensive, scientifically accurate answer that would be helpful for researchers, conservationists, or students interested in marine science.`;

    return this.generateContent(prompt);
  }

  async getMarineInsights(): Promise<string> {
    const prompt = `As a marine biology expert, provide current insights about marine biodiversity and conservation. Please discuss:

1. Current major trends in marine biodiversity
2. Key challenges facing marine ecosystems
3. Recent conservation success stories
4. Emerging threats to ocean health
5. Actionable recommendations for marine protection

Please provide practical, science-based insights that would be valuable for researchers and conservationists.`;

    return this.generateContent(prompt);
  }
}

// Get API key from environment variables
const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY || '';

export const geminiApi = new GeminiApiService(GEMINI_API_KEY);